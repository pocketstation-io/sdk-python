use std::collections::HashMap;

use pocketstation::connector::ConnectorSecret;
use pocketstation::{
    AudioCaps, BackpressurePolicy, BinaryFormat, ChannelLayout, Codec, CopyPolicy,
    DerivedStreamHandle, EdgeContract, EndpointConfiguration, EndpointDescriptor, EndpointHandle,
    EventFormat, MediaCaps, Multiplicity, Operator, OperatorConfiguration, OperatorId,
    OperatorInputHandle, OperatorInstanceHandle, PortDirection, PortSpec, SampleFormat,
    SignalClass, SignalSpec, SourceConfiguration, SourceInstanceHandle, SourceOutputHandle,
    SourceTypeId, StemHandle, TextFormat,
};
use pocketstation_relay::{RelayPublishReceiptKey, RelayRouteConfiguration};
use pyo3::exceptions::{PyRuntimeError, PyValueError};
use pyo3::prelude::*;

use crate::errors::{coded_reason, session_error, validate_nonempty};
use crate::relay::{PythonRelayPublisher, RelayRouteRegistration};

fn invalid_contract(reason: impl Into<String>) -> PyErr {
    PyValueError::new_err(coded_reason("graph.invalid_contract", reason.into()))
}

fn parse_codec(value: &str) -> PyResult<Codec> {
    match value {
        "opus" => Ok(Codec::Opus),
        "aac" => Ok(Codec::Aac),
        "mp3" => Ok(Codec::Mp3),
        "g711-ulaw" => Ok(Codec::G711Ulaw),
        "g711-alaw" => Ok(Codec::G711Alaw),
        "webm-opus" => Ok(Codec::WebmOpus),
        _ => Err(invalid_contract(format!("unsupported codec {value:?}"))),
    }
}

const fn codec_name(value: Codec) -> &'static str {
    match value {
        Codec::Opus => "opus",
        Codec::Aac => "aac",
        Codec::Mp3 => "mp3",
        Codec::G711Ulaw => "g711-ulaw",
        Codec::G711Alaw => "g711-alaw",
        Codec::WebmOpus => "webm-opus",
    }
}

fn parse_text_format(value: &str) -> PyResult<TextFormat> {
    match value {
        "utf8" => Ok(TextFormat::Utf8),
        "json" => Ok(TextFormat::Json),
        "markdown" => Ok(TextFormat::Markdown),
        _ => Err(invalid_contract(format!(
            "unsupported text format {value:?}"
        ))),
    }
}

const fn text_format_name(value: TextFormat) -> &'static str {
    match value {
        TextFormat::Utf8 => "utf8",
        TextFormat::Json => "json",
        TextFormat::Markdown => "markdown",
    }
}

fn parse_event_format(value: &str) -> PyResult<EventFormat> {
    match value {
        "json" => Ok(EventFormat::Json),
        "protobuf" => Ok(EventFormat::Protobuf),
        "flatbuffers" => Ok(EventFormat::Flatbuffers),
        "cbor" => Ok(EventFormat::Cbor),
        _ => Err(invalid_contract(format!(
            "unsupported event format {value:?}"
        ))),
    }
}

const fn event_format_name(value: EventFormat) -> &'static str {
    match value {
        EventFormat::Json => "json",
        EventFormat::Protobuf => "protobuf",
        EventFormat::Flatbuffers => "flatbuffers",
        EventFormat::Cbor => "cbor",
    }
}

fn parse_binary_format(value: &str) -> PyResult<BinaryFormat> {
    match value {
        "raw" => Ok(BinaryFormat::Raw),
        "protobuf" => Ok(BinaryFormat::Protobuf),
        "flatbuffers" => Ok(BinaryFormat::Flatbuffers),
        "cbor" => Ok(BinaryFormat::Cbor),
        _ => Err(invalid_contract(format!(
            "unsupported binary format {value:?}"
        ))),
    }
}

const fn binary_format_name(value: BinaryFormat) -> &'static str {
    match value {
        BinaryFormat::Raw => "raw",
        BinaryFormat::Protobuf => "protobuf",
        BinaryFormat::Flatbuffers => "flatbuffers",
        BinaryFormat::Cbor => "cbor",
    }
}

fn parse_channel_layout(value: &str) -> PyResult<ChannelLayout> {
    match value {
        "mono" => Ok(ChannelLayout::Mono),
        "stereo" => Ok(ChannelLayout::Stereo),
        "any" => Ok(ChannelLayout::Any),
        _ => Err(invalid_contract(format!(
            "unsupported channel layout {value:?}"
        ))),
    }
}

const fn channel_layout_name(value: ChannelLayout) -> &'static str {
    match value {
        ChannelLayout::Mono => "mono",
        ChannelLayout::Stereo => "stereo",
        ChannelLayout::Any => "any",
    }
}

fn parse_backpressure(value: &str) -> PyResult<BackpressurePolicy> {
    match value {
        "drop-newest" => Ok(BackpressurePolicy::DropNewest),
        "drop-oldest" => Ok(BackpressurePolicy::DropOldest),
        "bounded-queue" => Ok(BackpressurePolicy::BoundedQueue),
        "block-forbidden" => Ok(BackpressurePolicy::BlockForbidden),
        _ => Err(invalid_contract(format!(
            "unsupported backpressure policy {value:?}"
        ))),
    }
}

const fn backpressure_name(value: BackpressurePolicy) -> &'static str {
    match value {
        BackpressurePolicy::DropNewest => "drop-newest",
        BackpressurePolicy::DropOldest => "drop-oldest",
        BackpressurePolicy::BoundedQueue => "bounded-queue",
        BackpressurePolicy::BlockForbidden => "block-forbidden",
    }
}

fn parse_copy_policy(value: &str) -> PyResult<CopyPolicy> {
    match value {
        "move-exclusive" => Ok(CopyPolicy::MoveExclusive),
        "share-read-only" => Ok(CopyPolicy::ShareReadOnly),
        "copy-to-branch-pool" => Ok(CopyPolicy::CopyToBranchPool),
        _ => Err(invalid_contract(format!(
            "unsupported copy policy {value:?}"
        ))),
    }
}

const fn copy_policy_name(value: CopyPolicy) -> &'static str {
    match value {
        CopyPolicy::MoveExclusive => "move-exclusive",
        CopyPolicy::ShareReadOnly => "share-read-only",
        CopyPolicy::CopyToBranchPool => "copy-to-branch-pool",
    }
}

fn make_configuration(values: HashMap<String, String>) -> OperatorConfiguration {
    values.into_iter().fold(
        OperatorConfiguration::new(),
        |configuration, (key, value)| configuration.with(&key, &value),
    )
}

pub(crate) fn make_operator(
    operator_id: String,
    configuration: HashMap<String, String>,
) -> Operator {
    Operator::new(
        OperatorId::new(operator_id),
        make_configuration(configuration),
    )
}

pub(crate) fn make_source_configuration(values: HashMap<String, String>) -> SourceConfiguration {
    let mut configuration = SourceConfiguration::default();
    for (key, value) in values {
        configuration.insert(key, value);
    }
    configuration
}

#[pyclass(name = "_SignalSpec", frozen)]
#[derive(Clone)]
pub(crate) struct PythonSignalSpec {
    pub(crate) value: SignalSpec,
}

#[pymethods]
impl PythonSignalSpec {
    #[new]
    #[pyo3(signature = (kind, format=None, custom_id=None, role=None, schema=None))]
    fn new(
        kind: String,
        format: Option<String>,
        custom_id: Option<String>,
        role: Option<String>,
        schema: Option<String>,
    ) -> PyResult<Self> {
        let mut value = match kind.as_str() {
            "any" => SignalSpec::any(),
            "pcm-audio" => SignalSpec::audio(),
            "encoded-audio" => SignalSpec::encoded_audio(parse_codec(
                format
                    .as_deref()
                    .ok_or_else(|| invalid_contract("encoded audio requires a codec"))?,
            )?),
            "text" => SignalSpec::text(parse_text_format(
                format
                    .as_deref()
                    .ok_or_else(|| invalid_contract("text requires a format"))?,
            )?),
            "event" => SignalSpec::event(parse_event_format(
                format
                    .as_deref()
                    .ok_or_else(|| invalid_contract("event requires a format"))?,
            )?),
            "metrics" => SignalSpec::metrics(),
            "control" => SignalSpec::control(),
            "binary" => SignalSpec::binary(parse_binary_format(
                format
                    .as_deref()
                    .ok_or_else(|| invalid_contract("binary requires a format"))?,
            )?),
            "custom" => SignalSpec::custom(
                custom_id.ok_or_else(|| invalid_contract("custom signal requires a stable ID"))?,
            ),
            _ => {
                return Err(invalid_contract(format!(
                    "unsupported signal kind {kind:?}"
                )))
            }
        };
        if let Some(role) = role {
            value = value.with_role(role);
        }
        if let Some(schema) = schema {
            value = value.with_schema(schema);
        }
        value
            .validate()
            .map_err(|error| invalid_contract(error.to_string()))?;
        Ok(Self { value })
    }

    #[getter]
    fn kind(&self) -> &'static str {
        match self.value.class() {
            SignalClass::Any => "any",
            SignalClass::PcmAudio => "pcm-audio",
            SignalClass::EncodedAudio(_) => "encoded-audio",
            SignalClass::Text(_) => "text",
            SignalClass::Event(_) => "event",
            SignalClass::Metrics => "metrics",
            SignalClass::Control => "control",
            SignalClass::Binary(_) => "binary",
            SignalClass::Custom(_) => "custom",
        }
    }

    #[getter]
    fn format(&self) -> Option<&'static str> {
        match self.value.class() {
            SignalClass::EncodedAudio(value) => Some(codec_name(*value)),
            SignalClass::Text(value) => Some(text_format_name(*value)),
            SignalClass::Event(value) => Some(event_format_name(*value)),
            SignalClass::Binary(value) => Some(binary_format_name(*value)),
            _ => None,
        }
    }

    #[getter]
    fn custom_id(&self) -> Option<String> {
        match self.value.class() {
            SignalClass::Custom(value) => Some(value.as_str().to_owned()),
            _ => None,
        }
    }

    #[getter]
    fn role(&self) -> Option<String> {
        self.value.role().map(|value| value.as_str().to_owned())
    }

    #[getter]
    fn schema(&self) -> Option<String> {
        self.value.schema().map(|value| value.as_str().to_owned())
    }

    #[getter]
    fn wire_id(&self) -> String {
        self.value.wire_id().to_owned()
    }

    #[getter]
    fn is_audio(&self) -> bool {
        self.value.class().is_audio()
    }

    fn is_compatible_with(&self, other: &Self) -> bool {
        self.value.is_compatible_with(&other.value)
    }
}

#[pyclass(name = "_MediaCaps", frozen)]
#[derive(Clone, Copy)]
pub(crate) struct PythonMediaCaps {
    pub(crate) value: MediaCaps,
}

#[pymethods]
impl PythonMediaCaps {
    #[new]
    #[pyo3(signature = (kind, format=None, sample_rate_hz=None, frame_samples=None, channel_layout=None))]
    fn new(
        kind: String,
        format: Option<String>,
        sample_rate_hz: Option<u32>,
        frame_samples: Option<usize>,
        channel_layout: Option<String>,
    ) -> PyResult<Self> {
        let value = match kind.as_str() {
            "audio-pcm" => MediaCaps::Audio(AudioCaps {
                sample_rate_hz,
                frame_samples,
                channel_layout: parse_channel_layout(channel_layout.as_deref().unwrap_or("any"))?,
                format: SampleFormat::F32Interleaved,
            }),
            "audio-encoded" => MediaCaps::EncodedAudio(parse_codec(
                format
                    .as_deref()
                    .ok_or_else(|| invalid_contract("encoded audio requires a codec"))?,
            )?),
            "text" => MediaCaps::Text,
            "event" => MediaCaps::Event,
            "metrics" => MediaCaps::Metrics,
            "control" => MediaCaps::Control,
            "binary" => MediaCaps::Binary(parse_binary_format(
                format
                    .as_deref()
                    .ok_or_else(|| invalid_contract("binary media requires a format"))?,
            )?),
            "any" => MediaCaps::Any,
            _ => return Err(invalid_contract(format!("unsupported media kind {kind:?}"))),
        };
        Ok(Self { value })
    }

    #[getter]
    fn kind(&self) -> &'static str {
        match self.value {
            MediaCaps::Audio(_) => "audio-pcm",
            MediaCaps::EncodedAudio(_) => "audio-encoded",
            MediaCaps::Text => "text",
            MediaCaps::Event => "event",
            MediaCaps::Metrics => "metrics",
            MediaCaps::Control => "control",
            MediaCaps::Binary(_) => "binary",
            MediaCaps::Any => "any",
        }
    }

    #[getter]
    fn format(&self) -> Option<&'static str> {
        match self.value {
            MediaCaps::Audio(_) => Some("f32-interleaved"),
            MediaCaps::EncodedAudio(value) => Some(codec_name(value)),
            MediaCaps::Binary(value) => Some(binary_format_name(value)),
            _ => None,
        }
    }

    #[getter]
    fn sample_rate_hz(&self) -> Option<u32> {
        match self.value {
            MediaCaps::Audio(value) => value.sample_rate_hz,
            _ => None,
        }
    }

    #[getter]
    fn frame_samples(&self) -> Option<usize> {
        match self.value {
            MediaCaps::Audio(value) => value.frame_samples,
            _ => None,
        }
    }

    #[getter]
    fn channel_layout(&self) -> Option<&'static str> {
        match self.value {
            MediaCaps::Audio(value) => Some(channel_layout_name(value.channel_layout)),
            _ => None,
        }
    }

    fn is_compatible_with(&self, other: &Self) -> bool {
        self.value.is_compatible_with(&other.value)
    }

    fn supports_signal(&self, signal: &PythonSignalSpec) -> bool {
        self.value.supports_signal(&signal.value)
    }
}

#[pyclass(name = "_PortSpec", frozen)]
#[derive(Clone)]
pub(crate) struct PythonPortSpec {
    pub(crate) value: PortSpec,
}

#[pymethods]
impl PythonPortSpec {
    #[new]
    fn new(
        name: String,
        direction: String,
        signal: &PythonSignalSpec,
        media: &PythonMediaCaps,
        multiplicity: String,
        required: bool,
    ) -> PyResult<Self> {
        let direction = match direction.as_str() {
            "input" => PortDirection::Input,
            "output" => PortDirection::Output,
            _ => return Err(invalid_contract("port direction must be input or output")),
        };
        let multiplicity = match multiplicity.as_str() {
            "one" => Multiplicity::One,
            "many" => Multiplicity::Many,
            _ => return Err(invalid_contract("port multiplicity must be one or many")),
        };
        PortSpec::new(
            name,
            direction,
            signal.value.clone(),
            media.value,
            multiplicity,
            required,
        )
        .map(|value| Self { value })
        .map_err(|error| invalid_contract(error.to_string()))
    }

    #[getter]
    fn name(&self) -> String {
        self.value.name().to_owned()
    }

    #[getter]
    fn direction(&self) -> &'static str {
        match self.value.direction() {
            PortDirection::Input => "input",
            PortDirection::Output => "output",
        }
    }

    #[getter]
    fn signal(&self) -> PythonSignalSpec {
        PythonSignalSpec {
            value: self.value.signal().clone(),
        }
    }

    #[getter]
    fn media(&self) -> PythonMediaCaps {
        PythonMediaCaps {
            value: self.value.media(),
        }
    }

    #[getter]
    fn multiplicity(&self) -> &'static str {
        match self.value.multiplicity() {
            Multiplicity::One => "one",
            Multiplicity::Many => "many",
        }
    }

    #[getter]
    fn required(&self) -> bool {
        self.value.required()
    }
}

#[pyclass(name = "_EdgeContract", frozen)]
#[derive(Clone, Copy)]
pub(crate) struct PythonEdgeContract {
    pub(crate) value: EdgeContract,
}

#[pymethods]
impl PythonEdgeContract {
    #[staticmethod]
    fn realtime_audio() -> Self {
        Self {
            value: EdgeContract::realtime_audio(),
        }
    }

    #[staticmethod]
    fn bounded_async() -> Self {
        Self {
            value: EdgeContract::bounded_async(),
        }
    }

    fn with_media(&self, media: &PythonMediaCaps) -> Self {
        Self {
            value: self.value.with_media(media.value),
        }
    }

    fn with_backpressure(&self, value: String) -> PyResult<Self> {
        Ok(Self {
            value: self.value.with_backpressure(parse_backpressure(&value)?),
        })
    }

    fn with_copy_policy(&self, value: String) -> PyResult<Self> {
        Ok(Self {
            value: self.value.with_copy_policy(parse_copy_policy(&value)?),
        })
    }

    fn with_jitter_budget_ms(&self, value: Option<u32>) -> Self {
        Self {
            value: self.value.with_jitter_budget_ms(value),
        }
    }

    fn with_max_payload_bytes(&self, value: usize) -> PyResult<Self> {
        Ok(Self {
            value: self.value.with_max_payload_bytes(value),
        })
    }

    #[getter]
    fn media(&self) -> PythonMediaCaps {
        PythonMediaCaps {
            value: self.value.media(),
        }
    }

    #[getter]
    fn clock(&self) -> &'static str {
        match self.value.clock() {
            pocketstation::ClockDomain::Capture => "capture",
            pocketstation::ClockDomain::Playback => "playback",
            pocketstation::ClockDomain::Network => "network",
            pocketstation::ClockDomain::Inherited => "inherited",
            pocketstation::ClockDomain::Wallclock => "wallclock",
        }
    }

    #[getter]
    fn latency_budget_ms(&self) -> Option<u32> {
        self.value.latency_budget_ms()
    }

    #[getter]
    fn jitter_budget_ms(&self) -> Option<u32> {
        self.value.jitter_budget_ms()
    }

    #[getter]
    fn backpressure(&self) -> &'static str {
        backpressure_name(self.value.backpressure())
    }

    #[getter]
    fn delivery(&self) -> &'static str {
        match self.value.delivery() {
            pocketstation::DeliverySemantics::BestEffortRealtime => "best-effort-realtime",
            pocketstation::DeliverySemantics::Ordered => "ordered",
            pocketstation::DeliverySemantics::ExactlyOnceNotRealtime => "exactly-once-not-realtime",
        }
    }

    #[getter]
    fn loss(&self) -> &'static str {
        match self.value.loss() {
            pocketstation::LossPolicy::ConcealForAudio => "conceal-for-audio",
            pocketstation::LossPolicy::MustDeliverOrFail => "must-deliver-or-fail",
            pocketstation::LossPolicy::DropAllowed => "drop-allowed",
        }
    }

    #[getter]
    fn copy_policy(&self) -> &'static str {
        copy_policy_name(self.value.copy_policy())
    }

    #[getter]
    fn observability(&self) -> &'static str {
        match self.value.observability() {
            pocketstation::EdgeObservabilityLevel::Off => "off",
            pocketstation::EdgeObservabilityLevel::Counters => "counters",
            pocketstation::EdgeObservabilityLevel::Full => "full",
        }
    }

    #[getter]
    fn max_payload_bytes(&self) -> Option<usize> {
        self.value.max_payload_bytes()
    }
}

#[pyclass(name = "_EndpointDescriptor", frozen)]
#[derive(Clone)]
pub(crate) struct PythonEndpointDescriptor {
    pub(crate) value: EndpointDescriptor,
}

#[pymethods]
impl PythonEndpointDescriptor {
    #[new]
    #[pyo3(signature = (node_type_id, operator_id, configuration, input_edge=None))]
    fn new(
        node_type_id: String,
        operator_id: String,
        configuration: HashMap<String, String>,
        input_edge: Option<&PythonEdgeContract>,
    ) -> PyResult<Self> {
        let configuration = configuration.into_iter().fold(
            EndpointConfiguration::new(),
            |configuration, (key, value)| configuration.with(key, value),
        );
        let mut value = EndpointDescriptor::new(
            pocketstation::NodeTypeId::from(node_type_id.as_str()),
            OperatorId::new(operator_id),
        )
        .with_configuration(configuration);
        if let Some(input_edge) = input_edge {
            value = value.with_input_edge(input_edge.value);
        }
        Ok(Self { value })
    }
}

#[pyclass(name = "Endpoint", frozen)]
pub(crate) struct PythonEndpoint {
    pub(crate) handle: EndpointHandle,
}

#[pymethods]
impl PythonEndpoint {
    #[getter]
    fn id(&self) -> u64 {
        self.handle.id().get()
    }

    #[getter]
    fn session_id(&self) -> u64 {
        self.handle.session_id().get()
    }

    #[getter]
    fn connector_id(&self) -> Option<u64> {
        self.handle
            .connector_id()
            .map(pocketstation::ConnectorId::get)
    }
}

#[pyclass(name = "OperatorInput", frozen)]
pub(crate) struct PythonOperatorInput {
    pub(crate) handle: OperatorInputHandle,
    port_name: String,
}

#[pymethods]
impl PythonOperatorInput {
    #[getter]
    fn port_name(&self) -> String {
        self.port_name.clone()
    }
}

#[pyclass(name = "OperatorInstance", frozen)]
pub(crate) struct PythonOperatorInstance {
    pub(crate) handle: OperatorInstanceHandle,
}

#[pymethods]
impl PythonOperatorInstance {
    #[getter]
    fn session_id(&self) -> u64 {
        self.handle.session_id().get()
    }

    #[getter]
    fn instance_id(&self) -> u64 {
        self.handle.instance_id().value()
    }

    fn input(&self, port_name: String) -> PyResult<PythonOperatorInput> {
        self.handle
            .input(port_name.clone())
            .map(|handle| PythonOperatorInput { handle, port_name })
            .map_err(session_error)
    }

    fn output(&self, port_name: String) -> PyResult<PythonDerivedStream> {
        self.handle
            .output(port_name)
            .map(|handle| PythonDerivedStream { handle })
            .map_err(session_error)
    }
}

fn publish_stem(
    handle: &StemHandle,
    publisher: &PythonRelayPublisher,
    bus_id: String,
) -> PyResult<u64> {
    publish_route(publisher, bus_id, |endpoint| {
        handle.send(endpoint).map_err(session_error)
    })
}

fn publish_source_output(
    handle: &SourceOutputHandle,
    publisher: &PythonRelayPublisher,
    bus_id: String,
) -> PyResult<u64> {
    publish_route(publisher, bus_id, |endpoint| {
        handle.send(endpoint).map_err(session_error)
    })
}

fn publish_route(
    publisher: &PythonRelayPublisher,
    bus_id: String,
    send: impl FnOnce(EndpointHandle) -> PyResult<pocketstation::RouteId>,
) -> PyResult<u64> {
    validate_nonempty("AudioBus ID", &bus_id)?;
    let configuration = RelayRouteConfiguration::new(
        &publisher.relay_url,
        &publisher.relay_session_id,
        ConnectorSecret::new(&publisher.source_token)
            .map_err(|error| PyValueError::new_err(error.to_string()))?,
        &bus_id,
    )
    .map_err(|error| PyValueError::new_err(error.to_string()))?;
    let mut routes = publisher
        .routes
        .lock()
        .map_err(|_| PyRuntimeError::new_err("relay route state is unavailable"))?;
    if routes.iter().any(|route| route.bus_id == bus_id) {
        return Err(PyValueError::new_err(coded_reason(
            "session.invalid_endpoint",
            "AudioBus IDs must be unique within one relay publisher",
        )));
    }
    let session = publisher
        .session
        .lock()
        .map_err(|_| PyRuntimeError::new_err("Session state is unavailable"))?;
    let session = session.as_ref().ok_or_else(|| {
        PyRuntimeError::new_err(coded_reason(
            pocketstation::SessionDeclarationErrorCode::DraftFrozen.as_str(),
            "Session has already started",
        ))
    })?;
    let endpoint = publisher
        .registered
        .declare(
            session,
            configuration
                .connector_configuration()
                .map_err(|error| PyValueError::new_err(error.to_string()))?,
            EdgeContract::realtime_audio(),
        )
        .map_err(|error| PyValueError::new_err(error.to_string()))?;
    let route_id = send(endpoint)?;
    let key = RelayPublishReceiptKey {
        endpoint_id: endpoint.id(),
        route_id,
    };
    routes.push(RelayRouteRegistration { bus_id, key });
    Ok(route_id.get())
}

#[pyclass(name = "Stem", frozen)]
pub(crate) struct PythonStem {
    pub(crate) handle: StemHandle,
}

#[pymethods]
impl PythonStem {
    fn send(&self, endpoint: &PythonEndpoint) -> PyResult<u64> {
        self.handle
            .send(endpoint.handle)
            .map(pocketstation::RouteId::get)
            .map_err(session_error)
    }

    fn send_to(&self, endpoint: &PythonEndpoint, input_port: Option<String>) -> PyResult<u64> {
        self.handle
            .send_to(endpoint.handle, input_port)
            .map(pocketstation::RouteId::get)
            .map_err(session_error)
    }

    fn connect(&self, input: &PythonOperatorInput) -> PyResult<u64> {
        self.handle
            .connect(input.handle.clone())
            .map(pocketstation::RouteId::get)
            .map_err(session_error)
    }

    #[pyo3(signature = (operator_id, configuration, input_port=None, output_port=None))]
    fn through(
        &self,
        operator_id: String,
        configuration: HashMap<String, String>,
        input_port: Option<String>,
        output_port: Option<String>,
    ) -> PyResult<PythonDerivedStream> {
        self.handle
            .through_ports(
                make_operator(operator_id, configuration),
                input_port,
                output_port,
            )
            .map(|handle| PythonDerivedStream { handle })
            .map_err(session_error)
    }

    fn record(&self, stem_name: String) -> PyResult<PythonEndpoint> {
        if stem_name.trim().is_empty() {
            return Err(PyValueError::new_err(coded_reason(
                "session.invalid_endpoint",
                "recording stem name must not be empty",
            )));
        }
        self.handle
            .record(stem_name)
            .map(|handle| PythonEndpoint { handle })
            .map_err(session_error)
    }

    fn publish(&self, publisher: &PythonRelayPublisher, bus_id: String) -> PyResult<u64> {
        publish_stem(&self.handle, publisher, bus_id)
    }

    #[getter]
    fn id(&self) -> u64 {
        self.handle.id().get()
    }

    #[getter]
    fn session_id(&self) -> u64 {
        self.handle.session_id().get()
    }
}

#[pyclass(name = "DerivedStream", frozen)]
pub(crate) struct PythonDerivedStream {
    pub(crate) handle: DerivedStreamHandle,
}

#[pymethods]
impl PythonDerivedStream {
    #[getter]
    fn session_id(&self) -> u64 {
        self.handle.session_id().get()
    }

    #[getter]
    fn operator_instance_id(&self) -> u64 {
        self.handle.operator_instance_id().value()
    }

    #[getter]
    fn output_port(&self) -> Option<String> {
        self.handle.output_port().map(str::to_owned)
    }

    fn output(&self, port_name: String) -> PyResult<Self> {
        self.handle
            .output(port_name)
            .map(|handle| Self { handle })
            .map_err(session_error)
    }

    fn connect(&self, input: &PythonOperatorInput) -> PyResult<u64> {
        self.handle
            .connect(input.handle.clone())
            .map(pocketstation::RouteId::get)
            .map_err(session_error)
    }

    #[pyo3(signature = (operator_id, configuration, input_port=None, output_port=None))]
    fn through(
        &self,
        operator_id: String,
        configuration: HashMap<String, String>,
        input_port: Option<String>,
        output_port: Option<String>,
    ) -> PyResult<Self> {
        self.handle
            .through_ports(
                make_operator(operator_id, configuration),
                input_port,
                output_port,
            )
            .map(|handle| Self { handle })
            .map_err(session_error)
    }

    fn send(&self, endpoint: &PythonEndpoint) -> PyResult<u64> {
        self.handle
            .send(endpoint.handle)
            .map(pocketstation::RouteId::get)
            .map_err(session_error)
    }

    fn send_to(&self, endpoint: &PythonEndpoint, input_port: Option<String>) -> PyResult<u64> {
        self.handle
            .send_to(endpoint.handle, input_port)
            .map(pocketstation::RouteId::get)
            .map_err(session_error)
    }

    fn reenter_audio(&self) -> PyResult<PythonStem> {
        self.handle
            .reenter_audio()
            .map(|handle| PythonStem { handle })
            .map_err(session_error)
    }
}

#[pyclass(name = "SourceInstance", frozen)]
pub(crate) struct PythonSourceInstance {
    pub(crate) handle: SourceInstanceHandle,
}

#[pymethods]
impl PythonSourceInstance {
    #[getter]
    fn session_id(&self) -> u64 {
        self.handle.session_id().get()
    }

    #[getter]
    fn instance_id(&self) -> u64 {
        self.handle.instance_id().value()
    }

    #[getter]
    fn source_id(&self) -> u64 {
        self.handle.source_id().get()
    }

    fn output(&self, port_name: String) -> PyResult<PythonSourceOutput> {
        self.handle
            .output(port_name)
            .map(|handle| PythonSourceOutput { handle })
            .map_err(session_error)
    }
}

#[pyclass(name = "SourceOutput", frozen)]
pub(crate) struct PythonSourceOutput {
    pub(crate) handle: SourceOutputHandle,
}

#[pymethods]
impl PythonSourceOutput {
    #[getter]
    fn session_id(&self) -> u64 {
        self.handle.session_id().get()
    }

    #[getter]
    fn source_instance_id(&self) -> u64 {
        self.handle.source_instance_id().value()
    }

    #[getter]
    fn source_id(&self) -> u64 {
        self.handle.source_id().get()
    }

    #[getter]
    fn stream_id(&self) -> u64 {
        self.handle.stream_id().get()
    }

    #[getter]
    fn output_port(&self) -> String {
        self.handle.output_port().to_owned()
    }

    fn connect(&self, input: &PythonOperatorInput) -> PyResult<u64> {
        self.handle
            .connect(input.handle.clone())
            .map(pocketstation::RouteId::get)
            .map_err(session_error)
    }

    #[pyo3(signature = (operator_id, configuration, input_port=None, output_port=None))]
    fn through(
        &self,
        operator_id: String,
        configuration: HashMap<String, String>,
        input_port: Option<String>,
        output_port: Option<String>,
    ) -> PyResult<PythonDerivedStream> {
        self.handle
            .through_ports(
                make_operator(operator_id, configuration),
                input_port,
                output_port,
            )
            .map(|handle| PythonDerivedStream { handle })
            .map_err(session_error)
    }

    fn send(&self, endpoint: &PythonEndpoint) -> PyResult<u64> {
        self.handle
            .send(endpoint.handle)
            .map(pocketstation::RouteId::get)
            .map_err(session_error)
    }

    fn send_to(&self, endpoint: &PythonEndpoint, input_port: Option<String>) -> PyResult<u64> {
        self.handle
            .send_to(endpoint.handle, input_port)
            .map(pocketstation::RouteId::get)
            .map_err(session_error)
    }

    fn record(&self, stem_name: String) -> PyResult<PythonEndpoint> {
        if stem_name.trim().is_empty() {
            return Err(PyValueError::new_err(coded_reason(
                "session.invalid_endpoint",
                "recording stem name must not be empty",
            )));
        }
        self.handle
            .record(stem_name)
            .map(|handle| PythonEndpoint { handle })
            .map_err(session_error)
    }

    fn publish(&self, publisher: &PythonRelayPublisher, bus_id: String) -> PyResult<u64> {
        publish_source_output(&self.handle, publisher, bus_id)
    }
}

pub(crate) fn make_source_type_id(value: String) -> PyResult<SourceTypeId> {
    SourceTypeId::new(value).map_err(|error| invalid_contract(error.to_string()))
}

#[cfg(feature = "conformance-fixtures")]
pub(crate) const GRAPH_CONFORMANCE_OPERATOR_ID: &str =
    "org.pocketstation.python.conformance.audio-pass-through.v1";
#[cfg(feature = "conformance-fixtures")]
const GRAPH_CONFORMANCE_NODE_ID: &str =
    "org.pocketstation.python.conformance.audio-pass-through-node.v1";
#[cfg(feature = "conformance-fixtures")]
pub(crate) const GRAPH_NONCONCRETE_OPERATOR_ID: &str =
    "org.pocketstation.python.conformance.nonconcrete-audio.v1";
#[cfg(feature = "conformance-fixtures")]
const GRAPH_NONCONCRETE_NODE_ID: &str =
    "org.pocketstation.python.conformance.nonconcrete-audio-node.v1";
#[cfg(feature = "conformance-fixtures")]
pub(crate) const GRAPH_TEXT_OPERATOR_ID: &str =
    "org.pocketstation.python.conformance.audio-to-text.v1";
#[cfg(feature = "conformance-fixtures")]
const GRAPH_TEXT_NODE_ID: &str = "org.pocketstation.python.conformance.audio-to-text-node.v1";
#[cfg(feature = "conformance-fixtures")]
pub(crate) const GRAPH_BYTES_OPERATOR_ID: &str =
    "org.pocketstation.python.conformance.audio-to-bytes.v1";
#[cfg(feature = "conformance-fixtures")]
const GRAPH_BYTES_NODE_ID: &str = "org.pocketstation.python.conformance.audio-to-bytes-node.v1";
#[cfg(feature = "conformance-fixtures")]
const GRAPH_CONFORMANCE_INPUT_PORT: &str = "audio-in";
#[cfg(feature = "conformance-fixtures")]
const GRAPH_CONFORMANCE_OUTPUT_PORT: &str = "audio-out";
#[cfg(feature = "conformance-fixtures")]
const GRAPH_TEXT_OUTPUT_PORT: &str = "text-out";
#[cfg(feature = "conformance-fixtures")]
const GRAPH_BYTES_OUTPUT_PORT: &str = "bytes-out";

#[cfg(feature = "conformance-fixtures")]
#[derive(Clone, Copy)]
enum GraphConformanceProjection {
    Audio,
    Text,
    Bytes,
}

#[cfg(feature = "conformance-fixtures")]
struct GraphConformanceOperatorFactory {
    manifest: pocketstation::AsyncOperatorManifest,
    projection: GraphConformanceProjection,
}

#[cfg(feature = "conformance-fixtures")]
struct GraphConformanceOperator {
    operator_id: OperatorId,
    projection: GraphConformanceProjection,
}

#[cfg(feature = "conformance-fixtures")]
impl pocketstation::AsyncNode for GraphConformanceOperator {
    fn prepare<'a>(
        &'a mut self,
        _context: &'a pocketstation::AsyncOperatorPrepareContext,
    ) -> pocketstation::AsyncNodeFuture<'a, Result<(), pocketstation::NodeError>> {
        Box::pin(async { Ok(()) })
    }

    fn process<'a>(
        &'a mut self,
        input: pocketstation::SignalEnvelope,
    ) -> pocketstation::AsyncNodeFuture<
        'a,
        Result<Vec<pocketstation::SignalEnvelope>, pocketstation::NodeError>,
    > {
        Box::pin(async move {
            let lineage = input.lineage().ok_or_else(|| {
                pocketstation::NodeError::Process(
                    "graph conformance audio input omitted Session lineage".to_owned(),
                )
            })?;
            let derivation = pocketstation::SignalDerivation::new(
                lineage,
                input.timing(),
                self.operator_id.clone(),
                1,
                1,
                None,
            )
            .map_err(|error| pocketstation::NodeError::Process(error.to_string()))?;
            let output = match self.projection {
                GraphConformanceProjection::Audio => input,
                GraphConformanceProjection::Text => {
                    let text = format!(
                        "source={} sequence={}",
                        lineage.source_id().get(),
                        lineage.sequence_number()
                    );
                    input.map_payload(
                        pocketstation::SignalPayload::Text(text),
                        SignalSpec::text(TextFormat::Utf8),
                    )
                }
                GraphConformanceProjection::Bytes => input.map_payload(
                    pocketstation::SignalPayload::Bytes(
                        lineage.sequence_number().to_le_bytes().to_vec(),
                    ),
                    SignalSpec::binary(BinaryFormat::Raw),
                ),
            };
            Ok(vec![output.with_derivation(derivation)])
        })
    }
}

#[cfg(feature = "conformance-fixtures")]
impl pocketstation::AsyncOperatorFactory for GraphConformanceOperatorFactory {
    fn manifest(&self) -> &pocketstation::AsyncOperatorManifest {
        &self.manifest
    }

    fn validate_config(
        &self,
        _configuration: &pocketstation::OperatorConfiguration,
    ) -> Result<(), pocketstation::ConfigError> {
        Ok(())
    }

    fn create(
        &self,
        _configuration: &pocketstation::OperatorConfiguration,
    ) -> Result<Box<dyn pocketstation::AsyncNode>, pocketstation::NodeError> {
        Ok(Box::new(GraphConformanceOperator {
            operator_id: self.manifest.operator_id().clone(),
            projection: self.projection,
        }))
    }
}

#[cfg(feature = "conformance-fixtures")]
pub(crate) fn register_graph_conformance_operator(
    session: &pocketstation::Session,
) -> Result<(), String> {
    use std::sync::Arc;

    let concrete_media = MediaCaps::Audio(AudioCaps {
        sample_rate_hz: Some(48_000),
        frame_samples: Some(960),
        channel_layout: ChannelLayout::Mono,
        format: SampleFormat::F32Interleaved,
    });
    let wildcard_media = MediaCaps::Audio(AudioCaps {
        sample_rate_hz: None,
        frame_samples: None,
        channel_layout: ChannelLayout::Any,
        format: SampleFormat::F32Interleaved,
    });
    for (manifest, projection) in [
        (
            graph_conformance_manifest(
                GRAPH_CONFORMANCE_OPERATOR_ID,
                GRAPH_CONFORMANCE_NODE_ID,
                "Python graph conformance audio pass-through",
                GRAPH_CONFORMANCE_OUTPUT_PORT,
                SignalSpec::audio(),
                concrete_media,
            )?,
            GraphConformanceProjection::Audio,
        ),
        (
            graph_conformance_manifest(
                GRAPH_NONCONCRETE_OPERATOR_ID,
                GRAPH_NONCONCRETE_NODE_ID,
                "Python graph conformance nonconcrete audio",
                GRAPH_CONFORMANCE_OUTPUT_PORT,
                SignalSpec::audio(),
                wildcard_media,
            )?,
            GraphConformanceProjection::Audio,
        ),
        (
            graph_conformance_manifest(
                GRAPH_TEXT_OPERATOR_ID,
                GRAPH_TEXT_NODE_ID,
                "Python graph conformance audio-to-text",
                GRAPH_TEXT_OUTPUT_PORT,
                SignalSpec::text(TextFormat::Utf8),
                MediaCaps::Text,
            )?,
            GraphConformanceProjection::Text,
        ),
        (
            graph_conformance_manifest(
                GRAPH_BYTES_OPERATOR_ID,
                GRAPH_BYTES_NODE_ID,
                "Python graph conformance audio-to-bytes",
                GRAPH_BYTES_OUTPUT_PORT,
                SignalSpec::binary(BinaryFormat::Raw),
                MediaCaps::Binary(BinaryFormat::Raw),
            )?,
            GraphConformanceProjection::Bytes,
        ),
    ] {
        session
            .register_operator(Arc::new(GraphConformanceOperatorFactory {
                manifest,
                projection,
            }))
            .map_err(|error| error.to_string())?;
    }
    Ok(())
}

#[cfg(feature = "conformance-fixtures")]
fn graph_conformance_manifest(
    operator_id: &'static str,
    node_id: &'static str,
    display_name: &'static str,
    output_port: &'static str,
    output_signal: SignalSpec,
    output_media: MediaCaps,
) -> Result<pocketstation::AsyncOperatorManifest, String> {
    let input_signal = SignalSpec::audio();
    let input_media = MediaCaps::Audio(AudioCaps {
        sample_rate_hz: Some(48_000),
        frame_samples: Some(960),
        channel_layout: ChannelLayout::Mono,
        format: SampleFormat::F32Interleaved,
    });
    let input = PortSpec::new(
        GRAPH_CONFORMANCE_INPUT_PORT,
        PortDirection::Input,
        input_signal,
        input_media,
        Multiplicity::Many,
        true,
    )
    .map_err(|error| error.to_string())?;
    let output = PortSpec::new(
        output_port,
        PortDirection::Output,
        output_signal,
        output_media,
        Multiplicity::Many,
        true,
    )
    .map_err(|error| error.to_string())?;
    let input_edge = EdgeContract::bounded_async()
        .with_media(input_media)
        .with_backpressure(BackpressurePolicy::DropNewest)
        .with_copy_policy(CopyPolicy::CopyToBranchPool);
    let output_edge = EdgeContract::bounded_async()
        .with_media(output_media)
        .with_copy_policy(CopyPolicy::CopyToBranchPool);
    pocketstation::AsyncOperatorManifest::new(
        OperatorId::new(operator_id),
        1,
        1,
        pocketstation::NodeDescriptor::new(
            pocketstation::NodeTypeId::from(node_id),
            display_name,
            vec![input],
            vec![output],
            pocketstation::ExecutionPartition::AsyncWorker,
            pocketstation::SafetyContract::AllocationAllowed,
            false,
        )
        .map_err(|error| error.to_string())?,
        input_edge,
        output_edge,
        16,
        pocketstation::OperatorPermissionPolicy {
            network_allowed: false,
            filesystem_allowed: false,
        },
        pocketstation::OperatorDeadlinePolicy {
            process_timeout_ms: 500,
        },
        pocketstation::OperatorCancellationPolicy::DiscardQueued,
        pocketstation::OperatorFailurePolicy::StopWorker,
        pocketstation::OperatorOutputRolePolicy::default(),
    )
    .map_err(|error| error.to_string())
}

pub(crate) fn register(module: &Bound<'_, PyModule>) -> PyResult<()> {
    module.add_class::<PythonSignalSpec>()?;
    module.add_class::<PythonMediaCaps>()?;
    module.add_class::<PythonPortSpec>()?;
    module.add_class::<PythonEdgeContract>()?;
    module.add_class::<PythonEndpointDescriptor>()?;
    module.add_class::<PythonEndpoint>()?;
    module.add_class::<PythonOperatorInput>()?;
    module.add_class::<PythonOperatorInstance>()?;
    module.add_class::<PythonStem>()?;
    module.add_class::<PythonDerivedStream>()?;
    module.add_class::<PythonSourceInstance>()?;
    module.add_class::<PythonSourceOutput>()?;
    Ok(())
}
