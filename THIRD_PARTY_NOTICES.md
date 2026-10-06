# Third-party licenses and notices

PocketStation SDK source is MIT licensed. Native wheels include the
components identified by their own CycloneDX SBOMs. This document
retains notices for the locked source build and six native targets;
each wheel's license expression describes only its listed components.

Linux repaired wheels additionally include libasound (LGPL-2.1-or-later),
libssl/libcrypto (Apache-2.0), and libpipewire (MIT). Exact corresponding
source RPM URLs and hashes are recorded below, including distribution
patches. The libraries remain separate shared objects and can be
replaced or rebuilt; the SDK does not restrict modification or reverse
engineering for debugging such modifications. ALSA's aserver and
PipeWire's libjackserver/libspa-alsa plugins are not bundled.

<!-- pocketstation-notice-index
{"components":[{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"aead","notice_origins":[{"origin":"crate:aead@0.5.2/LICENSE-APACHE","sha256":"b1cf9a3333ca78152b859012cd4a804156e5243e9ca20ad1df7327ba5ea7405c"},{"origin":"crate:aead@0.5.2/LICENSE-MIT","sha256":"949ab7b3e7140fee216f06fe3a2bd67d68dd511f8ea73c1e01c98cb348e9c8ae"}],"notices":["949ab7b3e7140fee216f06fe3a2bd67d68dd511f8ea73c1e01c98cb348e9c8ae","b1cf9a3333ca78152b859012cd4a804156e5243e9ca20ad1df7327ba5ea7405c"],"source_url":"https://crates.io/api/v1/crates/aead/0.5.2/download","version":"0.5.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"aes","notice_origins":[{"origin":"crate:aes@0.8.4/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:aes@0.8.4/LICENSE-MIT","sha256":"f7e8ab639afef15573680c97f796166835cbeb3865175882fea41c60d106b733"}],"notices":["a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5","f7e8ab639afef15573680c97f796166835cbeb3865175882fea41c60d106b733"],"source_url":"https://crates.io/api/v1/crates/aes/0.8.4/download","version":"0.8.4"},{"ecosystem":"cargo","license_expression":"Unlicense OR MIT","name":"aho-corasick","notice_origins":[{"origin":"crate:aho-corasick@1.1.5/COPYING","sha256":"01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f"},{"origin":"crate:aho-corasick@1.1.5/LICENSE-MIT","sha256":"0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f"}],"notices":["01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f","0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f"],"source_url":"https://crates.io/api/v1/crates/aho-corasick/1.1.5/download","version":"1.1.5"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"alsa","notice_origins":[{"origin":"crate:alsa@0.11.0/LICENSE-APACHE","sha256":"0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594"},{"origin":"crate:alsa@0.11.0/LICENSE-MIT","sha256":"3cc33f8e76680b9cba2e2a5bc94de5a92420045863ab2fadbef290a55b4d8530"}],"notices":["0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594","3cc33f8e76680b9cba2e2a5bc94de5a92420045863ab2fadbef290a55b4d8530"],"source_url":"https://crates.io/api/v1/crates/alsa/0.11.0/download","version":"0.11.0"},{"ecosystem":"cargo","license_expression":"MIT","name":"alsa-sys","notice_origins":[{"origin":"crate:alsa-sys@0.4.0/LICENSE","sha256":"219766b3420f49f6204143c5f3ef750888fb6de29ce5f63e909f146e90b375a2"}],"notices":["219766b3420f49f6204143c5f3ef750888fb6de29ce5f63e909f146e90b375a2"],"source_url":"https://crates.io/api/v1/crates/alsa-sys/0.4.0/download","version":"0.4.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"annotate-snippets","notice_origins":[{"origin":"crate:annotate-snippets@0.11.5/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:annotate-snippets@0.11.5/LICENSE-MIT","sha256":"6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6"}],"notices":["6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/annotate-snippets/0.11.5/download","version":"0.11.5"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"anstyle","notice_origins":[{"origin":"crate:anstyle@1.0.14/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:anstyle@1.0.14/LICENSE-MIT","sha256":"6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6"}],"notices":["6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/anstyle/1.0.14/download","version":"1.0.14"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"anyhow","notice_origins":[{"origin":"crate:anyhow@1.0.104/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:anyhow@1.0.104/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/crates/anyhow/1.0.104","version":"1.0.104"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"arrayvec","notice_origins":[{"origin":"crate:arrayvec@0.7.8/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:arrayvec@0.7.8/LICENSE-MIT","sha256":"4da95ec4ecb65b738d470b7d762894ad9c97da93e6cbfb18b570fc2c96f4b871"}],"notices":["4da95ec4ecb65b738d470b7d762894ad9c97da93e6cbfb18b570fc2c96f4b871","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/arrayvec/0.7.8/download","version":"0.7.8"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"asn1-rs","notice_origins":[{"origin":"crate:asn1-rs@0.7.2/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:asn1-rs@0.7.2/LICENSE-MIT","sha256":"a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513"}],"notices":["a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/asn1-rs/0.7.2/download","version":"0.7.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"asn1-rs-derive","notice_origins":[{"origin":"crate:asn1-rs-derive@0.6.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:asn1-rs-derive@0.6.0/LICENSE-MIT","sha256":"a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513"}],"notices":["a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/asn1-rs-derive/0.6.0/download","version":"0.6.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"asn1-rs-impl","notice_origins":[{"origin":"https://raw.githubusercontent.com/rusticata/asn1-rs/a20e5f7319c896737ad0f2557037817b91ad854f/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"https://raw.githubusercontent.com/rusticata/asn1-rs/a20e5f7319c896737ad0f2557037817b91ad854f/LICENSE-MIT","sha256":"a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513"}],"notices":["a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/asn1-rs-impl/0.2.0/download","version":"0.2.0"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"autocfg","notice_origins":[{"origin":"crate:autocfg@1.5.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:autocfg@1.5.1/LICENSE-MIT","sha256":"27995d58ad5c1145c1a8cd86244ce844886958a35eb2b78c6b772748669999ac"}],"notices":["27995d58ad5c1145c1a8cd86244ce844886958a35eb2b78c6b772748669999ac","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/autocfg/1.5.1/download","version":"1.5.1"},{"ecosystem":"cargo","license_expression":"MIT","name":"autotools","notice_origins":[{"origin":"crate:autotools@0.2.7/LICENSE","sha256":"334c40cc7ab76303a1555e77724200631cf31c2a3846b2602161cf8921210b46"}],"notices":["334c40cc7ab76303a1555e77724200631cf31c2a3846b2602161cf8921210b46"],"source_url":"https://crates.io/crates/autotools/0.2.7","version":"0.2.7"},{"ecosystem":"cargo","license_expression":"ISC AND (Apache-2.0 OR ISC)","name":"aws-lc-rs","notice_origins":[{"origin":"crate:aws-lc-rs@1.18.1/LICENSE","sha256":"b50b376e7d24a0598488b730c3034ffcd0b58dd36c0913a24b9903a3cfd04bf7"}],"notices":["b50b376e7d24a0598488b730c3034ffcd0b58dd36c0913a24b9903a3cfd04bf7"],"source_url":"https://crates.io/api/v1/crates/aws-lc-rs/1.18.1/download","version":"1.18.1"},{"ecosystem":"cargo","license_expression":"ISC AND (Apache-2.0 OR ISC) AND Apache-2.0 AND MIT AND BSD-3-Clause AND (Apache-2.0 OR ISC OR MIT) AND (Apache-2.0 OR ISC OR MIT-0)","name":"aws-lc-sys","notice_origins":[{"origin":"crate:aws-lc-sys@0.45.0/LICENSE","sha256":"728536b4160e051f86d7c9c388f704866b3d512cd7df97ac3516c65279523c4e"},{"origin":"crate:aws-lc-sys@0.45.0/aws-lc/LICENSE","sha256":"977c541bd25ffe36975dde25c028c0cd15ddf3d08243983b58e8a6a3d9447523"},{"origin":"crate:aws-lc-sys@0.45.0/aws-lc/third_party/fiat/LICENSE","sha256":"43e358d7b6eb109d0f51f7b3a090fd82607965767c25fadee39e922475de2061"}],"notices":["43e358d7b6eb109d0f51f7b3a090fd82607965767c25fadee39e922475de2061","728536b4160e051f86d7c9c388f704866b3d512cd7df97ac3516c65279523c4e","977c541bd25ffe36975dde25c028c0cd15ddf3d08243983b58e8a6a3d9447523"],"source_url":"https://crates.io/api/v1/crates/aws-lc-sys/0.45.0/download","version":"0.45.0"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"base16ct","notice_origins":[{"origin":"crate:base16ct@0.2.0/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:base16ct@0.2.0/LICENSE-MIT","sha256":"0aa8963e105e8b6e02f634484145d4e5b0f42d0a6dd05c16f8148f033383adef"}],"notices":["0aa8963e105e8b6e02f634484145d4e5b0f42d0a6dd05c16f8148f033383adef","a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"],"source_url":"https://crates.io/api/v1/crates/base16ct/0.2.0/download","version":"0.2.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"base64","notice_origins":[{"origin":"crate:base64@0.22.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:base64@0.22.1/LICENSE-MIT","sha256":"0dd882e53de11566d50f8e8e2d5a651bcf3fabee4987d70f306233cf39094ba7"}],"notices":["0dd882e53de11566d50f8e8e2d5a651bcf3fabee4987d70f306233cf39094ba7","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/base64/0.22.1/download","version":"0.22.1"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"base64ct","notice_origins":[{"origin":"crate:base64ct@1.8.3/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:base64ct@1.8.3/LICENSE-MIT","sha256":"2d1c57bff28344b9e698f51063bc8509799cc4c99a4e0cf2aa3f7e7c3e1f9a9d"}],"notices":["2d1c57bff28344b9e698f51063bc8509799cc4c99a4e0cf2aa3f7e7c3e1f9a9d","a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"],"source_url":"https://crates.io/api/v1/crates/base64ct/1.8.3/download","version":"1.8.3"},{"ecosystem":"cargo","license_expression":"BSD-3-Clause","name":"bindgen","notice_origins":[{"origin":"crate:bindgen@0.72.1/LICENSE","sha256":"c23953d9deb0a3312dbeaf6c128a657f3591acee45067612fa68405eaa4525db"}],"notices":["c23953d9deb0a3312dbeaf6c128a657f3591acee45067612fa68405eaa4525db"],"source_url":"https://crates.io/api/v1/crates/bindgen/0.72.1/download","version":"0.72.1"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"bit-vec","notice_origins":[{"origin":"crate:bit-vec@0.9.1/LICENSE-APACHE","sha256":"8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90"},{"origin":"crate:bit-vec@0.9.1/LICENSE-MIT","sha256":"f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7"}],"notices":["8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90","f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7"],"source_url":"https://crates.io/api/v1/crates/bit-vec/0.9.1/download","version":"0.9.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"bitflags","notice_origins":[{"origin":"crate:bitflags@2.13.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:bitflags@2.13.1/LICENSE-MIT","sha256":"6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb"}],"notices":["6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/bitflags/2.13.1/download","version":"2.13.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"block-buffer","notice_origins":[{"origin":"crate:block-buffer@0.10.4/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:block-buffer@0.10.4/LICENSE-MIT","sha256":"d5c22aa3118d240e877ad41c5d9fa232f9c77d757d4aac0c2f943afc0a95e0ef"}],"notices":["a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5","d5c22aa3118d240e877ad41c5d9fa232f9c77d757d4aac0c2f943afc0a95e0ef"],"source_url":"https://crates.io/api/v1/crates/block-buffer/0.10.4/download","version":"0.10.4"},{"ecosystem":"cargo","license_expression":"MIT","name":"block2","notice_origins":[{"origin":"https://raw.githubusercontent.com/madsmtm/objc2/b4167b582b2f75f9a1be75495c41b765344fd03c/LICENSE.md","sha256":"7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"}],"notices":["7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"],"source_url":"https://crates.io/api/v1/crates/block2/0.6.2/download","version":"0.6.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"bumpalo","notice_origins":[{"origin":"crate:bumpalo@3.20.3/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:bumpalo@3.20.3/LICENSE-MIT","sha256":"65f94e99ddaf4f5d1782a6dae23f35d4293a9a01444a13135a6887017d353cee"}],"notices":["65f94e99ddaf4f5d1782a6dae23f35d4293a9a01444a13135a6887017d353cee","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/bumpalo/3.20.3/download","version":"3.20.3"},{"ecosystem":"cargo","license_expression":"MIT","name":"bytes","notice_origins":[{"origin":"crate:bytes@1.12.1/LICENSE","sha256":"45f522cacecb1023856e46df79ca625dfc550c94910078bd8aec6e02880b3d42"}],"notices":["45f522cacecb1023856e46df79ca625dfc550c94910078bd8aec6e02880b3d42"],"source_url":"https://crates.io/api/v1/crates/bytes/1.12.1/download","version":"1.12.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"cc","notice_origins":[{"origin":"crate:cc@1.4.5/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:cc@1.4.5/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/cc/1.4.5/download","version":"1.4.5"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"ccm","notice_origins":[{"origin":"crate:ccm@0.5.0/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:ccm@0.5.0/LICENSE-MIT","sha256":"904801faf3f1850328af8e1aa1047b9190cc22ed40df5c87f2d93d17f847ef67"}],"notices":["904801faf3f1850328af8e1aa1047b9190cc22ed40df5c87f2d93d17f847ef67","a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"],"source_url":"https://crates.io/api/v1/crates/ccm/0.5.0/download","version":"0.5.0"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"cexpr","notice_origins":[{"origin":"crate:cexpr@0.6.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:cexpr@0.6.0/LICENSE-MIT","sha256":"d9771b8c6cf4426d3846de54c1febe20907f1eeadf7adfb5ade89a83bd9ea77f"}],"notices":["a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2","d9771b8c6cf4426d3846de54c1febe20907f1eeadf7adfb5ade89a83bd9ea77f"],"source_url":"https://crates.io/api/v1/crates/cexpr/0.6.0/download","version":"0.6.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"cfg-expr","notice_origins":[{"origin":"crate:cfg-expr@0.20.9/LICENSE-APACHE","sha256":"8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90"},{"origin":"crate:cfg-expr@0.20.9/LICENSE-MIT","sha256":"090a294a492ab2f41388252312a65cf2f0e423330b721a68c6665ac64766753b"}],"notices":["090a294a492ab2f41388252312a65cf2f0e423330b721a68c6665ac64766753b","8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90"],"source_url":"https://crates.io/api/v1/crates/cfg-expr/0.20.9/download","version":"0.20.9"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"cfg-if","notice_origins":[{"origin":"crate:cfg-if@1.0.4/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:cfg-if@1.0.4/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/cfg-if/1.0.4/download","version":"1.0.4"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"cipher","notice_origins":[{"origin":"crate:cipher@0.4.4/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:cipher@0.4.4/LICENSE-MIT","sha256":"5c7bd92d1f096f12203dc1b601e3cb17484fa1b023e30b6b8edcc80e416237ec"}],"notices":["5c7bd92d1f096f12203dc1b601e3cb17484fa1b023e30b6b8edcc80e416237ec","a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"],"source_url":"https://crates.io/api/v1/crates/cipher/0.4.4/download","version":"0.4.4"},{"ecosystem":"cargo","license_expression":"Apache-2.0","name":"clang-sys","notice_origins":[{"origin":"crate:clang-sys@1.9.1/LICENSE.txt","sha256":"cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"}],"notices":["cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"],"source_url":"https://crates.io/api/v1/crates/clang-sys/1.9.1/download","version":"1.9.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"cmake","notice_origins":[{"origin":"crate:cmake@0.1.58/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:cmake@0.1.58/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/cmake/0.1.58/download","version":"0.1.58"},{"ecosystem":"cargo","license_expression":"MIT","name":"combine","notice_origins":[{"origin":"crate:combine@4.6.8/LICENSE","sha256":"9bbc1b3dc4674a9ebb12c2a62f54fe3c08672539717f8d05828f684b6cc419a3"}],"notices":["9bbc1b3dc4674a9ebb12c2a62f54fe3c08672539717f8d05828f684b6cc419a3"],"source_url":"https://crates.io/api/v1/crates/combine/4.6.8/download","version":"4.6.8"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"const-oid","notice_origins":[{"origin":"crate:const-oid@0.9.6/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:const-oid@0.9.6/LICENSE-MIT","sha256":"bada9e7ed8dc00d63502053c455d7c8d7575dfb7e8277a2a832531844d900682"}],"notices":["a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5","bada9e7ed8dc00d63502053c455d7c8d7575dfb7e8277a2a832531844d900682"],"source_url":"https://crates.io/api/v1/crates/const-oid/0.9.6/download","version":"0.9.6"},{"ecosystem":"cargo","license_expression":"MIT","name":"cookie-factory","notice_origins":[{"origin":"https://raw.githubusercontent.com/rust-bakery/cookie-factory/d36b805dbd7dd65f2df947235c5bcc573afe2c76/.reuse/dep5","sha256":"fac95e33eb175ff151cde39e3f7ad52292e6acf83db22bef30d3bfad417a8846"},{"origin":"https://raw.githubusercontent.com/rust-bakery/cookie-factory/d36b805dbd7dd65f2df947235c5bcc573afe2c76/LICENSES/MIT.txt","sha256":"d09216dc1ea5f273997667935a8d6514d80f00b89fb6954ecc3a43e0a6e360de"}],"notices":["d09216dc1ea5f273997667935a8d6514d80f00b89fb6954ecc3a43e0a6e360de","fac95e33eb175ff151cde39e3f7ad52292e6acf83db22bef30d3bfad417a8846"],"source_url":"https://crates.io/api/v1/crates/cookie-factory/0.3.3/download","version":"0.3.3"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"core-foundation","notice_origins":[{"origin":"crate:core-foundation@0.10.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:core-foundation@0.10.1/LICENSE-MIT","sha256":"62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3"}],"notices":["62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/core-foundation/0.10.1/download","version":"0.10.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"core-foundation-sys","notice_origins":[{"origin":"crate:core-foundation-sys@0.8.7/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:core-foundation-sys@0.8.7/LICENSE-MIT","sha256":"62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3"}],"notices":["62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/core-foundation-sys/0.8.7/download","version":"0.8.7"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"coreaudio-rs","notice_origins":[{"origin":"crate:coreaudio-rs@0.14.2/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:coreaudio-rs@0.14.2/LICENSE-MIT","sha256":"7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545"}],"notices":["7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/coreaudio-rs/0.14.2/download","version":"0.14.2"},{"ecosystem":"cargo","license_expression":"Apache-2.0","name":"cpal","notice_origins":[{"origin":"crate:cpal@0.18.2/LICENSE","sha256":"c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"}],"notices":["c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"],"source_url":"https://crates.io/api/v1/crates/cpal/0.18.2/download","version":"0.18.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"cpufeatures","notice_origins":[{"origin":"crate:cpufeatures@0.2.17/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:cpufeatures@0.2.17/LICENSE-MIT","sha256":"ae9baa7beea910273c2f384c2a6b721fb7bd02bda3436074a1072e4ee689f985"}],"notices":["a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5","ae9baa7beea910273c2f384c2a6b721fb7bd02bda3436074a1072e4ee689f985"],"source_url":"https://crates.io/api/v1/crates/cpufeatures/0.2.17/download","version":"0.2.17"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"crc","notice_origins":[{"origin":"crate:crc@3.4.0/LICENSE-APACHE","sha256":"470355a7eed93fcc4281ec2e0f82ca3b94e7af1e4d83629f91de8cfac34d750e"},{"origin":"crate:crc@3.4.0/LICENSE-MIT","sha256":"3488679340a49ecc34d342c4009d2dabf76f4a21f12aec2ca99b15805d656544"}],"notices":["3488679340a49ecc34d342c4009d2dabf76f4a21f12aec2ca99b15805d656544","470355a7eed93fcc4281ec2e0f82ca3b94e7af1e4d83629f91de8cfac34d750e"],"source_url":"https://crates.io/api/v1/crates/crc/3.4.0/download","version":"3.4.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"crc-catalog","notice_origins":[{"origin":"crate:crc-catalog@2.5.0/LICENSES/Apache-2.0.txt","sha256":"d3cdb764b98283ee7c3a3cea8d374e2a2957322374378d1f3263f4d512741fc3"},{"origin":"crate:crc-catalog@2.5.0/LICENSES/MIT.txt","sha256":"5ef8fcfb6cccec8fcae043c834099a60c8b7406408db576e026d2b7e67dc5cf5"}],"notices":["5ef8fcfb6cccec8fcae043c834099a60c8b7406408db576e026d2b7e67dc5cf5","d3cdb764b98283ee7c3a3cea8d374e2a2957322374378d1f3263f4d512741fc3"],"source_url":"https://crates.io/api/v1/crates/crc-catalog/2.5.0/download","version":"2.5.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"crypto-common","notice_origins":[{"origin":"crate:crypto-common@0.1.7/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:crypto-common@0.1.7/LICENSE-MIT","sha256":"3521672491a3479422d5fe1aca6645dd2984090f85da6e5205abfb18fb7a6897"}],"notices":["3521672491a3479422d5fe1aca6645dd2984090f85da6e5205abfb18fb7a6897","a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"],"source_url":"https://crates.io/api/v1/crates/crypto-common/0.1.7/download","version":"0.1.7"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"ctr","notice_origins":[{"origin":"crate:ctr@0.9.2/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:ctr@0.9.2/LICENSE-MIT","sha256":"63af4bea227c94d021e99427f6ca3a4b8efddadcca93ab6130f708cf6138cf68"}],"notices":["63af4bea227c94d021e99427f6ca3a4b8efddadcca93ab6130f708cf6138cf68","a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"],"source_url":"https://crates.io/api/v1/crates/ctr/0.9.2/download","version":"0.9.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"dasp_sample","notice_origins":[{"origin":"https://raw.githubusercontent.com/rustaudio/sample/97c3bb9b2363c0b46ac1633858bf1054fd02a980/LICENSE-APACHE","sha256":"756c8d2ab2dc24f256e1455b5f03937f4933d83d7bc9f2d55009fc962377d512"},{"origin":"https://raw.githubusercontent.com/rustaudio/sample/97c3bb9b2363c0b46ac1633858bf1054fd02a980/LICENSE-MIT","sha256":"b1d6df41ed3aa96806e74c729444d7c121d90e6660a6aed01d298e03fde475a0"}],"notices":["756c8d2ab2dc24f256e1455b5f03937f4933d83d7bc9f2d55009fc962377d512","b1d6df41ed3aa96806e74c729444d7c121d90e6660a6aed01d298e03fde475a0"],"source_url":"https://crates.io/api/v1/crates/dasp_sample/0.11.0/download","version":"0.11.0"},{"ecosystem":"cargo","license_expression":"MIT","name":"data-encoding","notice_origins":[{"origin":"crate:data-encoding@2.11.1/LICENSE","sha256":"b68ad1a3367b825447089e1f8d6829b97f47a89eb78d2f4ebaef4672f5606186"}],"notices":["b68ad1a3367b825447089e1f8d6829b97f47a89eb78d2f4ebaef4672f5606186"],"source_url":"https://crates.io/api/v1/crates/data-encoding/2.11.1/download","version":"2.11.1"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"der","notice_origins":[{"origin":"crate:der@0.7.10/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:der@0.7.10/LICENSE-MIT","sha256":"ad64fcb9589f162720f3cc5010ad76ca6ad3764e11861f9192c489df176bb71d"}],"notices":["a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5","ad64fcb9589f162720f3cc5010ad76ca6ad3764e11861f9192c489df176bb71d"],"source_url":"https://crates.io/api/v1/crates/der/0.7.10/download","version":"0.7.10"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"der-parser","notice_origins":[{"origin":"crate:der-parser@10.0.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:der-parser@10.0.0/LICENSE-MIT","sha256":"a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513"}],"notices":["a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/der-parser/10.0.0/download","version":"10.0.0"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"der_derive","notice_origins":[{"origin":"crate:der_derive@0.7.3/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:der_derive@0.7.3/LICENSE-MIT","sha256":"bada9e7ed8dc00d63502053c455d7c8d7575dfb7e8277a2a832531844d900682"}],"notices":["a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5","bada9e7ed8dc00d63502053c455d7c8d7575dfb7e8277a2a832531844d900682"],"source_url":"https://crates.io/api/v1/crates/der_derive/0.7.3/download","version":"0.7.3"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"deranged","notice_origins":[{"origin":"crate:deranged@0.5.8/LICENSE-Apache","sha256":"edd65bdd88957a205c47d53fa499eed8865a70320f0f03f6391668cb304ea376"},{"origin":"crate:deranged@0.5.8/LICENSE-MIT","sha256":"231c837c45eb53f108fb48929e488965bc4fcc14e9ea21d35f50e6b99d98685b"}],"notices":["231c837c45eb53f108fb48929e488965bc4fcc14e9ea21d35f50e6b99d98685b","edd65bdd88957a205c47d53fa499eed8865a70320f0f03f6391668cb304ea376"],"source_url":"https://crates.io/api/v1/crates/deranged/0.5.8/download","version":"0.5.8"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"digest","notice_origins":[{"origin":"crate:digest@0.10.7/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:digest@0.10.7/LICENSE-MIT","sha256":"9e0dfd2dd4173a530e238cb6adb37aa78c34c6bc7444e0e10c1ab5d8881f63ba"}],"notices":["9e0dfd2dd4173a530e238cb6adb37aa78c34c6bc7444e0e10c1ab5d8881f63ba","a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"],"source_url":"https://crates.io/api/v1/crates/digest/0.10.7/download","version":"0.10.7"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"dimpl","notice_origins":[{"origin":"crate:dimpl@0.6.2/LICENSE-APACHE.txt","sha256":"c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"},{"origin":"crate:dimpl@0.6.2/LICENSE-MIT.txt","sha256":"5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b"}],"notices":["5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b","c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"],"source_url":"https://crates.io/api/v1/crates/dimpl/0.6.2/download","version":"0.6.2"},{"ecosystem":"cargo","license_expression":"Zlib OR Apache-2.0 OR MIT","name":"dispatch2","notice_origins":[{"origin":"https://raw.githubusercontent.com/madsmtm/objc2/8852b424193ca41602281b3d7540d7c8ed51e49a/LICENSE.md","sha256":"7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"}],"notices":["7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"],"source_url":"https://crates.io/api/v1/crates/dispatch2/0.3.1/download","version":"0.3.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"displaydoc","notice_origins":[{"origin":"crate:displaydoc@0.2.7/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:displaydoc@0.2.7/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/displaydoc/0.2.7/download","version":"0.2.7"},{"ecosystem":"cargo","license_expression":"CC0-1.0 OR MIT-0 OR Apache-2.0","name":"dunce","notice_origins":[{"origin":"crate:dunce@1.0.5/LICENSE","sha256":"a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499"}],"notices":["a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499"],"source_url":"https://crates.io/api/v1/crates/dunce/1.0.5/download","version":"1.0.5"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"either","notice_origins":[{"origin":"crate:either@1.18.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:either@1.18.0/LICENSE-MIT","sha256":"7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545"}],"notices":["7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/either/1.18.0/download","version":"1.18.0"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"equivalent","notice_origins":[{"origin":"crate:equivalent@1.0.2/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:equivalent@1.0.2/LICENSE-MIT","sha256":"7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349"}],"notices":["7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/equivalent/1.0.2/download","version":"1.0.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"errno","notice_origins":[{"origin":"crate:errno@0.3.14/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:errno@0.3.14/LICENSE-MIT","sha256":"8764a597675778ddfd4e25f81b08a05dbcf089ac05662df7613fe67f150e3aa2"}],"notices":["8764a597675778ddfd4e25f81b08a05dbcf089ac05662df7613fe67f150e3aa2","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/errno/0.3.14/download","version":"0.3.14"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"fastrand","notice_origins":[{"origin":"crate:fastrand@2.5.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:fastrand@2.5.0/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/fastrand/2.5.0/download","version":"2.5.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"find-msvc-tools","notice_origins":[{"origin":"crate:find-msvc-tools@0.1.12/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:find-msvc-tools@0.1.12/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/find-msvc-tools/0.1.12/download","version":"0.1.12"},{"ecosystem":"cargo","license_expression":"Apache-2.0","name":"flagset","notice_origins":[{"origin":"crate:flagset@0.4.7/LICENSE","sha256":"cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"}],"notices":["cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"],"source_url":"https://crates.io/api/v1/crates/flagset/0.4.7/download","version":"0.4.7"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"foreign-types","notice_origins":[{"origin":"crate:foreign-types@0.3.2/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:foreign-types@0.3.2/LICENSE-MIT","sha256":"333ea3aaa3cadb819f4acd9f9153f9feee060a995ca8710f32bc5bd9a4b91734"}],"notices":["333ea3aaa3cadb819f4acd9f9153f9feee060a995ca8710f32bc5bd9a4b91734","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/foreign-types/0.3.2/download","version":"0.3.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"foreign-types-shared","notice_origins":[{"origin":"crate:foreign-types-shared@0.1.1/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:foreign-types-shared@0.1.1/LICENSE-MIT","sha256":"333ea3aaa3cadb819f4acd9f9153f9feee060a995ca8710f32bc5bd9a4b91734"}],"notices":["333ea3aaa3cadb819f4acd9f9153f9feee060a995ca8710f32bc5bd9a4b91734","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/foreign-types-shared/0.1.1/download","version":"0.1.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"form_urlencoded","notice_origins":[{"origin":"crate:form_urlencoded@1.2.2/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:form_urlencoded@1.2.2/LICENSE-MIT","sha256":"20c7855c364d57ea4c97889a5e8d98470a9952dade37bd9248b9a54431670e5e"}],"notices":["20c7855c364d57ea4c97889a5e8d98470a9952dade37bd9248b9a54431670e5e","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/form_urlencoded/1.2.2/download","version":"1.2.2"},{"ecosystem":"cargo","license_expression":"MIT","name":"fs_extra","notice_origins":[{"origin":"crate:fs_extra@1.3.0/LICENSE","sha256":"251ea8ccb1205ce5fa847d6e264d6b6753af62de2cecf2fd9abc0eb02c7c83fc"}],"notices":["251ea8ccb1205ce5fa847d6e264d6b6753af62de2cecf2fd9abc0eb02c7c83fc"],"source_url":"https://crates.io/api/v1/crates/fs_extra/1.3.0/download","version":"1.3.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"futures-core","notice_origins":[{"origin":"crate:futures-core@0.3.34/LICENSE-APACHE","sha256":"275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427"},{"origin":"crate:futures-core@0.3.34/LICENSE-MIT","sha256":"6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd"}],"notices":["275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427","6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd"],"source_url":"https://crates.io/api/v1/crates/futures-core/0.3.34/download","version":"0.3.34"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"futures-task","notice_origins":[{"origin":"crate:futures-task@0.3.34/LICENSE-APACHE","sha256":"275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427"},{"origin":"crate:futures-task@0.3.34/LICENSE-MIT","sha256":"6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd"}],"notices":["275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427","6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd"],"source_url":"https://crates.io/api/v1/crates/futures-task/0.3.34/download","version":"0.3.34"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"futures-util","notice_origins":[{"origin":"crate:futures-util@0.3.34/LICENSE-APACHE","sha256":"275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427"},{"origin":"crate:futures-util@0.3.34/LICENSE-MIT","sha256":"6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd"}],"notices":["275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427","6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd"],"source_url":"https://crates.io/api/v1/crates/futures-util/0.3.34/download","version":"0.3.34"},{"ecosystem":"cargo","license_expression":"MIT","name":"generic-array","notice_origins":[{"origin":"crate:generic-array@0.14.7/LICENSE","sha256":"c09aae9d3c77b531f56351a9947bc7446511d6b025b3255312d3e3442a9a7583"}],"notices":["c09aae9d3c77b531f56351a9947bc7446511d6b025b3255312d3e3442a9a7583"],"source_url":"https://crates.io/api/v1/crates/generic-array/0.14.7/download","version":"0.14.7"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"getrandom","notice_origins":[{"origin":"crate:getrandom@0.3.4/LICENSE-APACHE","sha256":"aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf"},{"origin":"crate:getrandom@0.3.4/LICENSE-MIT","sha256":"29e9fe5074bd27e0e5d5d110394fbbcd841baee2651a3c4b4560a632702cede4"}],"notices":["29e9fe5074bd27e0e5d5d110394fbbcd841baee2651a3c4b4560a632702cede4","aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf"],"source_url":"https://crates.io/api/v1/crates/getrandom/0.3.4/download","version":"0.3.4"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"getrandom","notice_origins":[{"origin":"crate:getrandom@0.4.3/LICENSE-APACHE","sha256":"aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf"},{"origin":"crate:getrandom@0.4.3/LICENSE-MIT","sha256":"523a42c25d245dde9c015f882cec7f4555aad883382a6cf19b4b7d9b2cd5419b"}],"notices":["523a42c25d245dde9c015f882cec7f4555aad883382a6cf19b4b7d9b2cd5419b","aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf"],"source_url":"https://crates.io/api/v1/crates/getrandom/0.4.3/download","version":"0.4.3"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"glob","notice_origins":[{"origin":"crate:glob@0.3.4/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:glob@0.3.4/LICENSE-MIT","sha256":"6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb"}],"notices":["6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/glob/0.3.4/download","version":"0.3.4"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"hashbrown","notice_origins":[{"origin":"crate:hashbrown@0.17.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:hashbrown@0.17.1/LICENSE-MIT","sha256":"ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2"}],"notices":["a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2","ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2"],"source_url":"https://crates.io/api/v1/crates/hashbrown/0.17.1/download","version":"0.17.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"heck","notice_origins":[{"origin":"crate:heck@0.5.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:heck@0.5.0/LICENSE-MIT","sha256":"7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0"}],"notices":["7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/heck/0.5.0/download","version":"0.5.0"},{"ecosystem":"cargo","license_expression":"Apache-2.0","name":"hound","notice_origins":[{"origin":"crate:hound@3.5.1/license","sha256":"cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"}],"notices":["cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"],"source_url":"https://crates.io/api/v1/crates/hound/3.5.1/download","version":"3.5.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"http","notice_origins":[{"origin":"crate:http@1.5.0/LICENSE-APACHE","sha256":"8bb1b50b0e5c9399ae33bd35fab2769010fa6c14e8860c729a52295d84896b7a"},{"origin":"crate:http@1.5.0/LICENSE-MIT","sha256":"dc91f8200e4b2a1f9261035d4c18c33c246911a6c0f7b543d75347e61b249cff"}],"notices":["8bb1b50b0e5c9399ae33bd35fab2769010fa6c14e8860c729a52295d84896b7a","dc91f8200e4b2a1f9261035d4c18c33c246911a6c0f7b543d75347e61b249cff"],"source_url":"https://crates.io/api/v1/crates/http/1.5.0/download","version":"1.5.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"httparse","notice_origins":[{"origin":"crate:httparse@1.10.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:httparse@1.10.1/LICENSE-MIT","sha256":"391a5396cec6230bfabd4ef4eb2350eb895bc5efce377a2218f5702ed020d3e3"}],"notices":["391a5396cec6230bfabd4ef4eb2350eb895bc5efce377a2218f5702ed020d3e3","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/httparse/1.10.1/download","version":"1.10.1"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"icu_collections","notice_origins":[{"origin":"crate:icu_collections@2.3.0/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/icu_collections/2.3.0/download","version":"2.3.0"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"icu_locale_core","notice_origins":[{"origin":"crate:icu_locale_core@2.3.0/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/icu_locale_core/2.3.0/download","version":"2.3.0"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"icu_normalizer","notice_origins":[{"origin":"crate:icu_normalizer@2.3.0/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/icu_normalizer/2.3.0/download","version":"2.3.0"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"icu_normalizer_data","notice_origins":[{"origin":"crate:icu_normalizer_data@2.3.0/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/icu_normalizer_data/2.3.0/download","version":"2.3.0"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"icu_properties","notice_origins":[{"origin":"crate:icu_properties@2.3.0/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/icu_properties/2.3.0/download","version":"2.3.0"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"icu_properties_data","notice_origins":[{"origin":"crate:icu_properties_data@2.3.0/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/icu_properties_data/2.3.0/download","version":"2.3.0"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"icu_provider","notice_origins":[{"origin":"crate:icu_provider@2.3.1/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/icu_provider/2.3.1/download","version":"2.3.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"idna","notice_origins":[{"origin":"crate:idna@1.1.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:idna@1.1.0/LICENSE-MIT","sha256":"b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5"}],"notices":["a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2","b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5"],"source_url":"https://crates.io/api/v1/crates/idna/1.1.0/download","version":"1.1.0"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"idna_adapter","notice_origins":[{"origin":"crate:idna_adapter@1.2.2/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:idna_adapter@1.2.2/LICENSE-MIT","sha256":"8b43ce8accd61e9d370b5ca9e9c4f953279b5c239926c62315b40e24df51b726"}],"notices":["8b43ce8accd61e9d370b5ca9e9c4f953279b5c239926c62315b40e24df51b726","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/idna_adapter/1.2.2/download","version":"1.2.2"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"indexmap","notice_origins":[{"origin":"crate:indexmap@2.14.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:indexmap@2.14.1/LICENSE-MIT","sha256":"ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055"}],"notices":["a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2","ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055"],"source_url":"https://crates.io/api/v1/crates/indexmap/2.14.1/download","version":"2.14.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"indoc","notice_origins":[{"origin":"crate:indoc@2.0.7/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:indoc@2.0.7/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/indoc/2.0.7/download","version":"2.0.7"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"inout","notice_origins":[{"origin":"crate:inout@0.1.4/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:inout@0.1.4/LICENSE-MIT","sha256":"304b898acad7f02e03d6d8832d682a3b43ee729ab5d3a069af5a36979083b6b4"}],"notices":["304b898acad7f02e03d6d8832d682a3b43ee729ab5d3a069af5a36979083b6b4","a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"],"source_url":"https://crates.io/api/v1/crates/inout/0.1.4/download","version":"0.1.4"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"is","notice_origins":[{"origin":"https://raw.githubusercontent.com/algesten/str0m/1905f2dbbde02964b5388a91dea9fb86ae7b0add/LICENSE-MIT.txt","sha256":"5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b"}],"notices":["5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b"],"source_url":"https://crates.io/api/v1/crates/is/0.9.1/download","version":"0.9.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"itertools","notice_origins":[{"origin":"crate:itertools@0.13.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:itertools@0.13.0/LICENSE-MIT","sha256":"7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545"}],"notices":["7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/itertools/0.13.0/download","version":"0.13.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"itoa","notice_origins":[{"origin":"crate:itoa@1.0.18/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:itoa@1.0.18/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/itoa/1.0.18/download","version":"1.0.18"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"jni","notice_origins":[{"origin":"https://raw.githubusercontent.com/jni-rs/jni-rs/5ae9458a4ec44c5318f37ddc7569c1d4ae8a69e7/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"https://raw.githubusercontent.com/jni-rs/jni-rs/5ae9458a4ec44c5318f37ddc7569c1d4ae8a69e7/LICENSE-MIT","sha256":"fea1d5bf3dd71605ce5d7d2ff695c1837e914c77195e523a86b5391716477960"}],"notices":["a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2","fea1d5bf3dd71605ce5d7d2ff695c1837e914c77195e523a86b5391716477960"],"source_url":"https://crates.io/api/v1/crates/jni/0.22.4/download","version":"0.22.4"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"jni-macros","notice_origins":[{"origin":"https://raw.githubusercontent.com/jni-rs/jni-rs/33045a124105c939d1e2cbdcb5a39e5d868ffa03/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"https://raw.githubusercontent.com/jni-rs/jni-rs/33045a124105c939d1e2cbdcb5a39e5d868ffa03/LICENSE-MIT","sha256":"fea1d5bf3dd71605ce5d7d2ff695c1837e914c77195e523a86b5391716477960"}],"notices":["a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2","fea1d5bf3dd71605ce5d7d2ff695c1837e914c77195e523a86b5391716477960"],"source_url":"https://crates.io/api/v1/crates/jni-macros/0.22.4/download","version":"0.22.4"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"jni-sys","notice_origins":[{"origin":"crate:jni-sys@0.3.1/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:jni-sys@0.3.1/LICENSE-MIT","sha256":"1d85bd754b04ceec93e98e890edd1fa3c6a22e81bcb32135806beeccefa51cd1"}],"notices":["1d85bd754b04ceec93e98e890edd1fa3c6a22e81bcb32135806beeccefa51cd1","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/jni-sys/0.3.1/download","version":"0.3.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"jni-sys","notice_origins":[{"origin":"crate:jni-sys@0.4.1/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:jni-sys@0.4.1/LICENSE-MIT","sha256":"1d85bd754b04ceec93e98e890edd1fa3c6a22e81bcb32135806beeccefa51cd1"}],"notices":["1d85bd754b04ceec93e98e890edd1fa3c6a22e81bcb32135806beeccefa51cd1","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/jni-sys/0.4.1/download","version":"0.4.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"jni-sys-macros","notice_origins":[{"origin":"https://raw.githubusercontent.com/jni-rs/jni-sys/64d77b7a5f119d7b55b4e2c169a4668067ff59e6/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"https://raw.githubusercontent.com/jni-rs/jni-sys/64d77b7a5f119d7b55b4e2c169a4668067ff59e6/LICENSE-MIT","sha256":"1d85bd754b04ceec93e98e890edd1fa3c6a22e81bcb32135806beeccefa51cd1"}],"notices":["1d85bd754b04ceec93e98e890edd1fa3c6a22e81bcb32135806beeccefa51cd1","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/jni-sys-macros/0.4.1/download","version":"0.4.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"jobserver","notice_origins":[{"origin":"crate:jobserver@0.1.35/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:jobserver@0.1.35/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/jobserver/0.1.35/download","version":"0.1.35"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"js-sys","notice_origins":[{"origin":"crate:js-sys@0.3.104/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:js-sys@0.3.104/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/js-sys/0.3.104/download","version":"0.3.104"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"lazy_static","notice_origins":[{"origin":"crate:lazy_static@1.5.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:lazy_static@1.5.0/LICENSE-MIT","sha256":"0621878e61f0d0fda054bcbe02df75192c28bde1ecc8289cbd86aeba2dd72720"}],"notices":["0621878e61f0d0fda054bcbe02df75192c28bde1ecc8289cbd86aeba2dd72720","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/lazy_static/1.5.0/download","version":"1.5.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"libc","notice_origins":[{"origin":"crate:libc@0.2.189/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:libc@0.2.189/LICENSE-MIT","sha256":"123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e"}],"notices":["123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/libc/0.2.189/download","version":"0.2.189"},{"ecosystem":"cargo","license_expression":"ISC","name":"libloading","notice_origins":[{"origin":"crate:libloading@0.8.9/LICENSE","sha256":"b29f8b01452350c20dd1af16ef83b598fea3053578ccc1c7a0ef40e57be2620f"}],"notices":["b29f8b01452350c20dd1af16ef83b598fea3053578ccc1c7a0ef40e57be2620f"],"source_url":"https://crates.io/api/v1/crates/libloading/0.8.9/download","version":"0.8.9"},{"ecosystem":"cargo","license_expression":"MIT","name":"libspa","notice_origins":[{"origin":"crate:libspa@0.10.1/LICENSE","sha256":"c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6"}],"notices":["c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6"],"source_url":"https://crates.io/api/v1/crates/libspa/0.10.1/download","version":"0.10.1"},{"ecosystem":"cargo","license_expression":"MIT","name":"libspa-sys","notice_origins":[{"origin":"crate:libspa-sys@0.10.1/LICENSE","sha256":"c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6"}],"notices":["c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6"],"source_url":"https://crates.io/api/v1/crates/libspa-sys/0.10.1/download","version":"0.10.1"},{"ecosystem":"cargo","license_expression":"Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT","name":"linux-raw-sys","notice_origins":[{"origin":"crate:linux-raw-sys@0.12.1/COPYRIGHT","sha256":"3290ae0fbc9ddb77d2239121d710f0bb9d31b3b4744e6d97fe01e652b4c1870b"},{"origin":"crate:linux-raw-sys@0.12.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:linux-raw-sys@0.12.1/LICENSE-Apache-2.0_WITH_LLVM-exception","sha256":"268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5"},{"origin":"crate:linux-raw-sys@0.12.1/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5","3290ae0fbc9ddb77d2239121d710f0bb9d31b3b4744e6d97fe01e652b4c1870b","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/linux-raw-sys/0.12.1/download","version":"0.12.1"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"litemap","notice_origins":[{"origin":"crate:litemap@0.8.3/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/litemap/0.8.3/download","version":"0.8.3"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"log","notice_origins":[{"origin":"crate:log@0.4.34/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:log@0.4.34/LICENSE-MIT","sha256":"6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb"}],"notices":["6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/log/0.4.34/download","version":"0.4.34"},{"ecosystem":"cargo","license_expression":"BSD-2-Clause OR MIT OR Apache-2.0","name":"mach2","notice_origins":[{"origin":"crate:mach2@0.6.0/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:mach2@0.6.0/LICENSE-BSD","sha256":"044983df14c97f2f9570766aaf977b3cdfc4a06cf1f36b776331c5ff89b4fb89"},{"origin":"crate:mach2@0.6.0/LICENSE-MIT","sha256":"3f9f0f7e5a5911a8042e32c83ff5d061ce1ffd02e8a207ec2135a44ad73b4191"}],"notices":["044983df14c97f2f9570766aaf977b3cdfc4a06cf1f36b776331c5ff89b4fb89","3f9f0f7e5a5911a8042e32c83ff5d061ce1ffd02e8a207ec2135a44ad73b4191","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/mach2/0.6.0/download","version":"0.6.0"},{"ecosystem":"cargo","license_expression":"Unlicense OR MIT","name":"memchr","notice_origins":[{"origin":"crate:memchr@2.8.3/COPYING","sha256":"01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f"},{"origin":"crate:memchr@2.8.3/LICENSE-MIT","sha256":"0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f"}],"notices":["01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f","0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f"],"source_url":"https://crates.io/api/v1/crates/memchr/2.8.3/download","version":"2.8.3"},{"ecosystem":"cargo","license_expression":"MIT","name":"memoffset","notice_origins":[{"origin":"crate:memoffset@0.9.1/LICENSE","sha256":"3234ac55816264ee7b6c7ee27efd61cf0a1fe775806870e3d9b4c41ea73c5cb1"}],"notices":["3234ac55816264ee7b6c7ee27efd61cf0a1fe775806870e3d9b4c41ea73c5cb1"],"source_url":"https://crates.io/api/v1/crates/memoffset/0.9.1/download","version":"0.9.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"minimal-lexical","notice_origins":[{"origin":"crate:minimal-lexical@0.2.1/LICENSE-APACHE","sha256":"8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90"},{"origin":"crate:minimal-lexical@0.2.1/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"},{"origin":"crate:minimal-lexical@0.2.1/LICENSE.md","sha256":"dbe1fff0fb1314b6af94f161511406275cf01c5a32441fbf24528a57a051d599"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90","dbe1fff0fb1314b6af94f161511406275cf01c5a32441fbf24528a57a051d599"],"source_url":"https://crates.io/api/v1/crates/minimal-lexical/0.2.1/download","version":"0.2.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"native-tls","notice_origins":[{"origin":"crate:native-tls@0.2.18/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:native-tls@0.2.18/LICENSE-MIT","sha256":"f2ad7982ddbfa8c45eb965315718c55b70b9cc311b49afacb50d5fe84173ae2c"}],"notices":["c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08","f2ad7982ddbfa8c45eb965315718c55b70b9cc311b49afacb50d5fe84173ae2c"],"source_url":"https://crates.io/api/v1/crates/native-tls/0.2.18/download","version":"0.2.18"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"ndk","notice_origins":[{"origin":"https://raw.githubusercontent.com/rust-mobile/ndk/49bbbba16c58ff63cb8a0ad0eca5a9fb7ecaec25/LICENSE-APACHE","sha256":"c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"},{"origin":"https://raw.githubusercontent.com/rust-mobile/ndk/49bbbba16c58ff63cb8a0ad0eca5a9fb7ecaec25/LICENSE-MIT","sha256":"508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1"}],"notices":["508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1","c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"],"source_url":"https://crates.io/api/v1/crates/ndk/0.9.0/download","version":"0.9.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"ndk-context","notice_origins":[{"origin":"https://raw.githubusercontent.com/rust-windowing/android-ndk-rs/10f2ba388fca20f7349996ebae26ccda7a6fda5c/LICENSE-APACHE","sha256":"c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"},{"origin":"https://raw.githubusercontent.com/rust-windowing/android-ndk-rs/10f2ba388fca20f7349996ebae26ccda7a6fda5c/LICENSE-MIT","sha256":"508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1"}],"notices":["508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1","c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"],"source_url":"https://crates.io/api/v1/crates/ndk-context/0.1.1/download","version":"0.1.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"ndk-sys","notice_origins":[{"origin":"https://raw.githubusercontent.com/rust-mobile/ndk/49bbbba16c58ff63cb8a0ad0eca5a9fb7ecaec25/LICENSE-APACHE","sha256":"c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"},{"origin":"https://raw.githubusercontent.com/rust-mobile/ndk/49bbbba16c58ff63cb8a0ad0eca5a9fb7ecaec25/LICENSE-MIT","sha256":"508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1"}],"notices":["508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1","c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4"],"source_url":"https://crates.io/api/v1/crates/ndk-sys/0.6.0+11769913/download","version":"0.6.0+11769913"},{"ecosystem":"cargo","license_expression":"MIT","name":"nom","notice_origins":[{"origin":"crate:nom@7.1.3/LICENSE","sha256":"4dbda04344456f09a7a588140455413a9ac59b6b26a1ef7cdf9c800c012d87f0"}],"notices":["4dbda04344456f09a7a588140455413a9ac59b6b26a1ef7cdf9c800c012d87f0"],"source_url":"https://crates.io/api/v1/crates/nom/7.1.3/download","version":"7.1.3"},{"ecosystem":"cargo","license_expression":"MIT","name":"nom","notice_origins":[{"origin":"crate:nom@8.0.0/LICENSE","sha256":"4dbda04344456f09a7a588140455413a9ac59b6b26a1ef7cdf9c800c012d87f0"}],"notices":["4dbda04344456f09a7a588140455413a9ac59b6b26a1ef7cdf9c800c012d87f0"],"source_url":"https://crates.io/api/v1/crates/nom/8.0.0/download","version":"8.0.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"num-bigint","notice_origins":[{"origin":"crate:num-bigint@0.4.8/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:num-bigint@0.4.8/LICENSE-MIT","sha256":"6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb"}],"notices":["6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/num-bigint/0.4.8/download","version":"0.4.8"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"num-conv","notice_origins":[{"origin":"crate:num-conv@0.2.2/LICENSE-Apache","sha256":"0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594"},{"origin":"crate:num-conv@0.2.2/LICENSE-MIT","sha256":"e2e245f2b566d0bfafb0f6a04c16b82d710c4e6e7d799e39bb4ef6e541b85b98"}],"notices":["0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594","e2e245f2b566d0bfafb0f6a04c16b82d710c4e6e7d799e39bb4ef6e541b85b98"],"source_url":"https://crates.io/api/v1/crates/num-conv/0.2.2/download","version":"0.2.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"num-derive","notice_origins":[{"origin":"crate:num-derive@0.4.2/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:num-derive@0.4.2/LICENSE-MIT","sha256":"6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb"}],"notices":["6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/num-derive/0.4.2/download","version":"0.4.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"num-integer","notice_origins":[{"origin":"crate:num-integer@0.1.47/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:num-integer@0.1.47/LICENSE-MIT","sha256":"6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb"}],"notices":["6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/num-integer/0.1.47/download","version":"0.1.47"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"num-traits","notice_origins":[{"origin":"crate:num-traits@0.2.19/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:num-traits@0.2.19/LICENSE-MIT","sha256":"6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb"}],"notices":["6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/num-traits/0.2.19/download","version":"0.2.19"},{"ecosystem":"cargo","license_expression":"BSD-3-Clause OR MIT OR Apache-2.0","name":"num_enum","notice_origins":[{"origin":"crate:num_enum@0.7.6/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:num_enum@0.7.6/LICENSE-BSD","sha256":"0be96d891d00e0ae0df75d7f3289b12871c000a1f5ac744f3b570768d4bb277c"},{"origin":"crate:num_enum@0.7.6/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["0be96d891d00e0ae0df75d7f3289b12871c000a1f5ac744f3b570768d4bb277c","23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/num_enum/0.7.6/download","version":"0.7.6"},{"ecosystem":"cargo","license_expression":"BSD-3-Clause OR MIT OR Apache-2.0","name":"num_enum_derive","notice_origins":[{"origin":"crate:num_enum_derive@0.7.6/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:num_enum_derive@0.7.6/LICENSE-BSD","sha256":"0be96d891d00e0ae0df75d7f3289b12871c000a1f5ac744f3b570768d4bb277c"},{"origin":"crate:num_enum_derive@0.7.6/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["0be96d891d00e0ae0df75d7f3289b12871c000a1f5ac744f3b570768d4bb277c","23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/num_enum_derive/0.7.6/download","version":"0.7.6"},{"ecosystem":"cargo","license_expression":"MIT","name":"objc2","notice_origins":[{"origin":"https://raw.githubusercontent.com/madsmtm/objc2/8852b424193ca41602281b3d7540d7c8ed51e49a/LICENSE.md","sha256":"7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"}],"notices":["7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"],"source_url":"https://crates.io/api/v1/crates/objc2/0.6.4/download","version":"0.6.4"},{"ecosystem":"cargo","license_expression":"Zlib OR Apache-2.0 OR MIT","name":"objc2-audio-toolbox","notice_origins":[{"origin":"https://raw.githubusercontent.com/madsmtm/objc2/7b1abfd750a2cacaea71d6a56ecfb83cb7de560b/LICENSE.md","sha256":"7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"}],"notices":["7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"],"source_url":"https://crates.io/api/v1/crates/objc2-audio-toolbox/0.3.2/download","version":"0.3.2"},{"ecosystem":"cargo","license_expression":"Zlib OR Apache-2.0 OR MIT","name":"objc2-avf-audio","notice_origins":[{"origin":"https://raw.githubusercontent.com/madsmtm/objc2/7b1abfd750a2cacaea71d6a56ecfb83cb7de560b/LICENSE.md","sha256":"7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"}],"notices":["7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"],"source_url":"https://crates.io/api/v1/crates/objc2-avf-audio/0.3.2/download","version":"0.3.2"},{"ecosystem":"cargo","license_expression":"Zlib OR Apache-2.0 OR MIT","name":"objc2-core-audio","notice_origins":[{"origin":"https://raw.githubusercontent.com/madsmtm/objc2/7b1abfd750a2cacaea71d6a56ecfb83cb7de560b/LICENSE.md","sha256":"7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"}],"notices":["7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"],"source_url":"https://crates.io/api/v1/crates/objc2-core-audio/0.3.2/download","version":"0.3.2"},{"ecosystem":"cargo","license_expression":"Zlib OR Apache-2.0 OR MIT","name":"objc2-core-audio-types","notice_origins":[{"origin":"https://raw.githubusercontent.com/madsmtm/objc2/7b1abfd750a2cacaea71d6a56ecfb83cb7de560b/LICENSE.md","sha256":"7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"}],"notices":["7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"],"source_url":"https://crates.io/api/v1/crates/objc2-core-audio-types/0.3.2/download","version":"0.3.2"},{"ecosystem":"cargo","license_expression":"Zlib OR Apache-2.0 OR MIT","name":"objc2-core-foundation","notice_origins":[{"origin":"https://raw.githubusercontent.com/madsmtm/objc2/7b1abfd750a2cacaea71d6a56ecfb83cb7de560b/LICENSE.md","sha256":"7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"}],"notices":["7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"],"source_url":"https://crates.io/api/v1/crates/objc2-core-foundation/0.3.2/download","version":"0.3.2"},{"ecosystem":"cargo","license_expression":"MIT","name":"objc2-encode","notice_origins":[{"origin":"https://raw.githubusercontent.com/madsmtm/objc2/8d214f5477365ffcbcbb7de058c86ed9a518efb7/LICENSE.md","sha256":"7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"}],"notices":["7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54"],"source_url":"https://crates.io/api/v1/crates/objc2-encode/4.1.0/download","version":"4.1.0"},{"ecosystem":"cargo","license_expression":"MIT","name":"objc2-foundation","notice_origins":[{"origin":"crate:objc2-foundation@0.3.2/src/copying.rs","sha256":"259b22f571b54fed25f68ec5abd8eda223e7b0547a806f13ba797a0eabecd64f"},{"origin":"crate:objc2-foundation@0.3.2/src/tests/copying.rs","sha256":"23d608079a47693a26dfc8a5cb01894ad0136a50714d46221d9380aa4a4b4423"}],"notices":["23d608079a47693a26dfc8a5cb01894ad0136a50714d46221d9380aa4a4b4423","259b22f571b54fed25f68ec5abd8eda223e7b0547a806f13ba797a0eabecd64f"],"source_url":"https://crates.io/api/v1/crates/objc2-foundation/0.3.2/download","version":"0.3.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"oid-registry","notice_origins":[{"origin":"crate:oid-registry@0.8.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:oid-registry@0.8.1/LICENSE-MIT","sha256":"a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513"}],"notices":["a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/oid-registry/0.8.1/download","version":"0.8.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"once_cell","notice_origins":[{"origin":"crate:once_cell@1.21.4/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:once_cell@1.21.4/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/once_cell/1.21.4/download","version":"1.21.4"},{"ecosystem":"cargo","license_expression":"Apache-2.0","name":"openssl","notice_origins":[{"origin":"crate:openssl@0.10.81/LICENSE","sha256":"f3d4287b4a21c5176fea2f9bd4ae800696004e2fb8e05cbc818be513f188a941"},{"origin":"crate:openssl@0.10.81/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"}],"notices":["c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08","f3d4287b4a21c5176fea2f9bd4ae800696004e2fb8e05cbc818be513f188a941"],"source_url":"https://crates.io/api/v1/crates/openssl/0.10.81/download","version":"0.10.81"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"openssl-macros","notice_origins":[{"origin":"crate:openssl-macros@0.1.1/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:openssl-macros@0.1.1/LICENSE-MIT","sha256":"ea5ab440900ab271811d5c2dc02a9de6e03a6956ac5727e85c11d76df5883d30"}],"notices":["c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08","ea5ab440900ab271811d5c2dc02a9de6e03a6956ac5727e85c11d76df5883d30"],"source_url":"https://crates.io/api/v1/crates/openssl-macros/0.1.1/download","version":"0.1.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"openssl-probe","notice_origins":[{"origin":"crate:openssl-probe@0.2.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:openssl-probe@0.2.1/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/openssl-probe/0.2.1/download","version":"0.2.1"},{"ecosystem":"cargo","license_expression":"MIT","name":"openssl-sys","notice_origins":[{"origin":"crate:openssl-sys@0.9.117/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"],"source_url":"https://crates.io/api/v1/crates/openssl-sys/0.9.117/download","version":"0.9.117"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"opus","notice_origins":[{"origin":"crate:opus@0.4.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:opus@0.4.0/LICENSE-MIT","sha256":"6b3b465fa69075348ee5ffc9ba6afa93402743a4a942a463404fac25257bd3ed"}],"notices":["6b3b465fa69075348ee5ffc9ba6afa93402743a4a942a463404fac25257bd3ed","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/opus/0.4.0/download","version":"0.4.0"},{"ecosystem":"cargo","license_expression":"BSD-3-Clause","name":"opusic-sys","notice_origins":[{"origin":"crate:opusic-sys@0.7.5/LICENSE","sha256":"01e1167d54a096d123cf6dfbbeb19587278845c6481d2d66d545669846079551"},{"origin":"crate:opusic-sys@0.7.5/opus/COPYING","sha256":"01e1167d54a096d123cf6dfbbeb19587278845c6481d2d66d545669846079551"}],"notices":["01e1167d54a096d123cf6dfbbeb19587278845c6481d2d66d545669846079551"],"source_url":"https://crates.io/api/v1/crates/opusic-sys/0.7.5/download","version":"0.7.5"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"pem-rfc7468","notice_origins":[{"origin":"crate:pem-rfc7468@0.7.0/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:pem-rfc7468@0.7.0/LICENSE-MIT","sha256":"90c503b61dee04e1449c323ec34c229dfb68d7adcb96c7e140ee55f70fce2d8e"}],"notices":["90c503b61dee04e1449c323ec34c229dfb68d7adcb96c7e140ee55f70fce2d8e","a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"],"source_url":"https://crates.io/api/v1/crates/pem-rfc7468/0.7.0/download","version":"0.7.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"percent-encoding","notice_origins":[{"origin":"crate:percent-encoding@2.3.2/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:percent-encoding@2.3.2/LICENSE-MIT","sha256":"b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5"}],"notices":["a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2","b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5"],"source_url":"https://crates.io/api/v1/crates/percent-encoding/2.3.2/download","version":"2.3.2"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"pin-project-lite","notice_origins":[{"origin":"crate:pin-project-lite@0.2.17/LICENSE-APACHE","sha256":"0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594"},{"origin":"crate:pin-project-lite@0.2.17/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594","23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"],"source_url":"https://crates.io/api/v1/crates/pin-project-lite/0.2.17/download","version":"0.2.17"},{"ecosystem":"cargo","license_expression":"MIT","name":"pipewire","notice_origins":[{"origin":"crate:pipewire@0.10.1/LICENSE","sha256":"c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6"}],"notices":["c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6"],"source_url":"https://crates.io/api/v1/crates/pipewire/0.10.1/download","version":"0.10.1"},{"ecosystem":"cargo","license_expression":"MIT","name":"pipewire-sys","notice_origins":[{"origin":"crate:pipewire-sys@0.10.1/LICENSE","sha256":"c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6"}],"notices":["c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6"],"source_url":"https://crates.io/api/v1/crates/pipewire-sys/0.10.1/download","version":"0.10.1"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"pkcs8","notice_origins":[{"origin":"crate:pkcs8@0.10.2/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:pkcs8@0.10.2/LICENSE-MIT","sha256":"ad64fcb9589f162720f3cc5010ad76ca6ad3764e11861f9192c489df176bb71d"}],"notices":["a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5","ad64fcb9589f162720f3cc5010ad76ca6ad3764e11861f9192c489df176bb71d"],"source_url":"https://crates.io/api/v1/crates/pkcs8/0.10.2/download","version":"0.10.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"pkg-config","notice_origins":[{"origin":"crate:pkg-config@0.3.34/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:pkg-config@0.3.34/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/pkg-config/0.3.34/download","version":"0.3.34"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"pocketstation","notice_origins":[{"origin":"crate:pocketstation@1.1.12/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:pocketstation@1.1.12/LICENSE-MIT","sha256":"37c1efe6301b127afb9d810c5fab62bdc60f72a7fb55f7a85ae00c0b8f6c1a42"}],"notices":["37c1efe6301b127afb9d810c5fab62bdc60f72a7fb55f7a85ae00c0b8f6c1a42","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/pocketstation/1.1.12/download","version":"1.1.12"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"pocketstation","notice_origins":[{"origin":"crate:pocketstation@1.1.13/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:pocketstation@1.1.13/LICENSE-MIT","sha256":"37c1efe6301b127afb9d810c5fab62bdc60f72a7fb55f7a85ae00c0b8f6c1a42"}],"notices":["37c1efe6301b127afb9d810c5fab62bdc60f72a7fb55f7a85ae00c0b8f6c1a42","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/pocketstation/1.1.13/download","version":"1.1.13"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"pocketstation-relay","notice_origins":[{"origin":"https://raw.githubusercontent.com/pocketstation-io/connectors/4f44eae11aebc3144db37c1867d9cf925a498165/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"https://raw.githubusercontent.com/pocketstation-io/connectors/4f44eae11aebc3144db37c1867d9cf925a498165/LICENSE-MIT","sha256":"37c1efe6301b127afb9d810c5fab62bdc60f72a7fb55f7a85ae00c0b8f6c1a42"}],"notices":["37c1efe6301b127afb9d810c5fab62bdc60f72a7fb55f7a85ae00c0b8f6c1a42","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/pocketstation-relay/0.1.5/download","version":"0.1.5"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"portable-atomic","notice_origins":[{"origin":"crate:portable-atomic@1.15.0/LICENSE-APACHE","sha256":"0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594"},{"origin":"crate:portable-atomic@1.15.0/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594","23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"],"source_url":"https://crates.io/api/v1/crates/portable-atomic/1.15.0/download","version":"1.15.0"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"potential_utf","notice_origins":[{"origin":"crate:potential_utf@0.1.6/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/potential_utf/0.1.6/download","version":"0.1.6"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"powerfmt","notice_origins":[{"origin":"crate:powerfmt@0.2.0/LICENSE-Apache","sha256":"155420c6403d4e0fca34105e3c03fdd6939b64c393c7ec6f95f5b72c5474eab0"},{"origin":"crate:powerfmt@0.2.0/LICENSE-MIT","sha256":"070dbc7dda03a29296f2d58bdb9b7331af90f2abc9f31df22875d1eabaf29852"}],"notices":["070dbc7dda03a29296f2d58bdb9b7331af90f2abc9f31df22875d1eabaf29852","155420c6403d4e0fca34105e3c03fdd6939b64c393c7ec6f95f5b72c5474eab0"],"source_url":"https://crates.io/api/v1/crates/powerfmt/0.2.0/download","version":"0.2.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"ppv-lite86","notice_origins":[{"origin":"crate:ppv-lite86@0.2.21/LICENSE-APACHE","sha256":"0218327e7a480793ffdd4eb792379a9709e5c135c7ba267f709d6f6d4d70af0a"},{"origin":"crate:ppv-lite86@0.2.21/LICENSE-MIT","sha256":"4cada0bd02ea3692eee6f16400d86c6508bbd3bafb2b65fed0419f36d4f83e8f"}],"notices":["0218327e7a480793ffdd4eb792379a9709e5c135c7ba267f709d6f6d4d70af0a","4cada0bd02ea3692eee6f16400d86c6508bbd3bafb2b65fed0419f36d4f83e8f"],"source_url":"https://crates.io/api/v1/crates/ppv-lite86/0.2.21/download","version":"0.2.21"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"prettyplease","notice_origins":[{"origin":"crate:prettyplease@0.2.37/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:prettyplease@0.2.37/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/crates/prettyplease/0.2.37","version":"0.2.37"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"proc-macro-crate","notice_origins":[{"origin":"crate:proc-macro-crate@3.5.0/LICENSE-APACHE","sha256":"8ada45cd9f843acf64e4722ae262c622a2b3b3007c7310ef36ac1061a30f6adb"},{"origin":"crate:proc-macro-crate@3.5.0/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","8ada45cd9f843acf64e4722ae262c622a2b3b3007c7310ef36ac1061a30f6adb"],"source_url":"https://crates.io/api/v1/crates/proc-macro-crate/3.5.0/download","version":"3.5.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"proc-macro2","notice_origins":[{"origin":"crate:proc-macro2@1.0.107/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:proc-macro2@1.0.107/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/proc-macro2/1.0.107/download","version":"1.0.107"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"pyo3","notice_origins":[{"origin":"crate:pyo3@0.27.2/LICENSE-APACHE","sha256":"32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9"},{"origin":"crate:pyo3@0.27.2/LICENSE-MIT","sha256":"afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6"},{"origin":"crate:pyo3@0.27.2/pyo3-runtime/LICENSE-APACHE","sha256":"32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9"},{"origin":"crate:pyo3@0.27.2/pyo3-runtime/LICENSE-MIT","sha256":"afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6"}],"notices":["32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9","afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6"],"source_url":"https://crates.io/api/v1/crates/pyo3/0.27.2/download","version":"0.27.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"pyo3-build-config","notice_origins":[{"origin":"crate:pyo3-build-config@0.27.2/LICENSE-APACHE","sha256":"32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9"},{"origin":"crate:pyo3-build-config@0.27.2/LICENSE-MIT","sha256":"afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6"}],"notices":["32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9","afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6"],"source_url":"https://crates.io/api/v1/crates/pyo3-build-config/0.27.2/download","version":"0.27.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"pyo3-ffi","notice_origins":[{"origin":"crate:pyo3-ffi@0.27.2/LICENSE-APACHE","sha256":"32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9"},{"origin":"crate:pyo3-ffi@0.27.2/LICENSE-MIT","sha256":"afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6"}],"notices":["32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9","afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6"],"source_url":"https://crates.io/api/v1/crates/pyo3-ffi/0.27.2/download","version":"0.27.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"pyo3-macros","notice_origins":[{"origin":"crate:pyo3-macros@0.27.2/LICENSE-APACHE","sha256":"32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9"},{"origin":"crate:pyo3-macros@0.27.2/LICENSE-MIT","sha256":"afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6"}],"notices":["32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9","afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6"],"source_url":"https://crates.io/api/v1/crates/pyo3-macros/0.27.2/download","version":"0.27.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"pyo3-macros-backend","notice_origins":[{"origin":"crate:pyo3-macros-backend@0.27.2/LICENSE-APACHE","sha256":"32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9"},{"origin":"crate:pyo3-macros-backend@0.27.2/LICENSE-MIT","sha256":"afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6"}],"notices":["32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9","afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6"],"source_url":"https://crates.io/api/v1/crates/pyo3-macros-backend/0.27.2/download","version":"0.27.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"quote","notice_origins":[{"origin":"crate:quote@1.0.47/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:quote@1.0.47/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/quote/1.0.47/download","version":"1.0.47"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0 OR LGPL-2.1-or-later","name":"r-efi","notice_origins":[{"origin":"crate:r-efi@5.3.0/AUTHORS","sha256":"ff92bed461f50338dd703a9ba9aee496a425957873df1d91192776e4bdf5dda7"}],"notices":["ff92bed461f50338dd703a9ba9aee496a425957873df1d91192776e4bdf5dda7"],"source_url":"https://crates.io/api/v1/crates/r-efi/5.3.0/download","version":"5.3.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0 OR LGPL-2.1-or-later","name":"r-efi","notice_origins":[{"origin":"crate:r-efi@6.0.0/AUTHORS","sha256":"d027e91dbc9cdbb2f1190068e498bd6b61cff022b6a032b191021ba658d96111"}],"notices":["d027e91dbc9cdbb2f1190068e498bd6b61cff022b6a032b191021ba658d96111"],"source_url":"https://crates.io/api/v1/crates/r-efi/6.0.0/download","version":"6.0.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"rand","notice_origins":[{"origin":"crate:rand@0.9.5/COPYRIGHT","sha256":"90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5"},{"origin":"crate:rand@0.9.5/LICENSE-APACHE","sha256":"35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab"},{"origin":"crate:rand@0.9.5/LICENSE-MIT","sha256":"209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b"}],"notices":["209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b","35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab","90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5"],"source_url":"https://crates.io/api/v1/crates/rand/0.9.5/download","version":"0.9.5"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"rand_chacha","notice_origins":[{"origin":"crate:rand_chacha@0.9.0/COPYRIGHT","sha256":"90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5"},{"origin":"crate:rand_chacha@0.9.0/LICENSE-APACHE","sha256":"35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab"},{"origin":"crate:rand_chacha@0.9.0/LICENSE-MIT","sha256":"209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b"}],"notices":["209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b","35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab","90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5"],"source_url":"https://crates.io/api/v1/crates/rand_chacha/0.9.0/download","version":"0.9.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"rand_core","notice_origins":[{"origin":"crate:rand_core@0.9.5/COPYRIGHT","sha256":"90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5"},{"origin":"crate:rand_core@0.9.5/LICENSE-APACHE","sha256":"6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51"},{"origin":"crate:rand_core@0.9.5/LICENSE-MIT","sha256":"209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b"}],"notices":["209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b","6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51","90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5"],"source_url":"https://crates.io/api/v1/crates/rand_core/0.9.5/download","version":"0.9.5"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"rcgen","notice_origins":[{"origin":"crate:rcgen@0.14.10/LICENSE","sha256":"debe6fed7ac143217c7f533759c54b14f18cd01d5fe195c51d83c2ae2d136cb4"}],"notices":["debe6fed7ac143217c7f533759c54b14f18cd01d5fe195c51d83c2ae2d136cb4"],"source_url":"https://crates.io/api/v1/crates/rcgen/0.14.10/download","version":"0.14.10"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"regex","notice_origins":[{"origin":"crate:regex@1.13.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:regex@1.13.1/LICENSE-MIT","sha256":"6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb"}],"notices":["6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/regex/1.13.1/download","version":"1.13.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"regex-automata","notice_origins":[{"origin":"crate:regex-automata@0.4.18/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:regex-automata@0.4.18/LICENSE-MIT","sha256":"6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb"}],"notices":["6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/regex-automata/0.4.18/download","version":"0.4.18"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"regex-syntax","notice_origins":[{"origin":"crate:regex-syntax@0.8.11/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:regex-syntax@0.8.11/LICENSE-MIT","sha256":"6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb"},{"origin":"crate:regex-syntax@0.8.11/src/unicode_tables/LICENSE-UNICODE","sha256":"74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3"}],"notices":["6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb","74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/regex-syntax/0.8.11/download","version":"0.8.11"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"rtrb","notice_origins":[{"origin":"crate:rtrb@0.3.5/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:rtrb@0.3.5/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/rtrb/0.3.5/download","version":"0.3.5"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"rustc-hash","notice_origins":[{"origin":"crate:rustc-hash@2.1.3/LICENSE-APACHE","sha256":"95bd3988beee069fa2848f648dab43cc6e0b2add2ad6bcb17360caf749802bcc"},{"origin":"crate:rustc-hash@2.1.3/LICENSE-MIT","sha256":"30fefc3a7d6a0041541858293bcbea2dde4caa4c0a5802f996a7f7e8c0085652"}],"notices":["30fefc3a7d6a0041541858293bcbea2dde4caa4c0a5802f996a7f7e8c0085652","95bd3988beee069fa2848f648dab43cc6e0b2add2ad6bcb17360caf749802bcc"],"source_url":"https://crates.io/api/v1/crates/rustc-hash/2.1.3/download","version":"2.1.3"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"rustc_version","notice_origins":[{"origin":"crate:rustc_version@0.4.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:rustc_version@0.4.1/LICENSE-MIT","sha256":"c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5"}],"notices":["a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2","c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5"],"source_url":"https://crates.io/api/v1/crates/rustc_version/0.4.1/download","version":"0.4.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"rusticata-macros","notice_origins":[{"origin":"crate:rusticata-macros@4.1.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:rusticata-macros@4.1.0/LICENSE-MIT","sha256":"a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513"}],"notices":["a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/rusticata-macros/4.1.0/download","version":"4.1.0"},{"ecosystem":"cargo","license_expression":"Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT","name":"rustix","notice_origins":[{"origin":"crate:rustix@1.1.4/COPYRIGHT","sha256":"377c2e7c53250cc5905c0b0532d35973392af16ffb9596a41d99d202cf3617c9"},{"origin":"crate:rustix@1.1.4/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:rustix@1.1.4/LICENSE-Apache-2.0_WITH_LLVM-exception","sha256":"268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5"},{"origin":"crate:rustix@1.1.4/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5","377c2e7c53250cc5905c0b0532d35973392af16ffb9596a41d99d202cf3617c9","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/rustix/1.1.4/download","version":"1.1.4"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"rustls-pki-types","notice_origins":[{"origin":"crate:rustls-pki-types@1.15.1/LICENSE-APACHE","sha256":"45fd05c4865e7c350b98ad7ac50e1b15462d49af4a91e9b0c9dd933dc9a69742"},{"origin":"crate:rustls-pki-types@1.15.1/LICENSE-MIT","sha256":"9117d922e667125508dde62b02c1f57ed22f5ad21eb536aa2e2d99e1c796e639"}],"notices":["45fd05c4865e7c350b98ad7ac50e1b15462d49af4a91e9b0c9dd933dc9a69742","9117d922e667125508dde62b02c1f57ed22f5ad21eb536aa2e2d99e1c796e639"],"source_url":"https://crates.io/api/v1/crates/rustls-pki-types/1.15.1/download","version":"1.15.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"rustversion","notice_origins":[{"origin":"crate:rustversion@1.0.23/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:rustversion@1.0.23/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/rustversion/1.0.23/download","version":"1.0.23"},{"ecosystem":"cargo","license_expression":"Unlicense OR MIT","name":"same-file","notice_origins":[{"origin":"crate:same-file@1.0.6/COPYING","sha256":"01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f"},{"origin":"crate:same-file@1.0.6/LICENSE-MIT","sha256":"cb3c929a05e6cbc9de9ab06a4c57eeb60ca8c724bef6c138c87d3a577e27aa14"}],"notices":["01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f","cb3c929a05e6cbc9de9ab06a4c57eeb60ca8c724bef6c138c87d3a577e27aa14"],"source_url":"https://crates.io/api/v1/crates/same-file/1.0.6/download","version":"1.0.6"},{"ecosystem":"cargo","license_expression":"MIT","name":"schannel","notice_origins":[{"origin":"crate:schannel@0.1.29/LICENSE.md","sha256":"aa72991ac35b4de0034da0afe943e62b48c4092fc2ba13ae47806d8e9a4ad551"}],"notices":["aa72991ac35b4de0034da0afe943e62b48c4092fc2ba13ae47806d8e9a4ad551"],"source_url":"https://crates.io/api/v1/crates/schannel/0.1.29/download","version":"0.1.29"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"sctp-proto","notice_origins":[{"origin":"crate:sctp-proto@0.9.1/LICENSE-APACHE","sha256":"814d11eba59f964bca7e74ef94f0d1eff1d5f322f895fb9b5d7e06f77debf3b2"},{"origin":"crate:sctp-proto@0.9.1/LICENSE-MIT","sha256":"7a6631daa22a9f1772e4a474ede9c3374a6c7a89b61c8b5973f7fd5ccd5cee8c"}],"notices":["7a6631daa22a9f1772e4a474ede9c3374a6c7a89b61c8b5973f7fd5ccd5cee8c","814d11eba59f964bca7e74ef94f0d1eff1d5f322f895fb9b5d7e06f77debf3b2"],"source_url":"https://crates.io/api/v1/crates/sctp-proto/0.9.1/download","version":"0.9.1"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"sec1","notice_origins":[{"origin":"crate:sec1@0.7.3/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:sec1@0.7.3/LICENSE-MIT","sha256":"4a883ecc3bb1010faed542bf63d53e530fea5e5e12cf676aed588784298ba929"}],"notices":["4a883ecc3bb1010faed542bf63d53e530fea5e5e12cf676aed588784298ba929","a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"],"source_url":"https://crates.io/api/v1/crates/sec1/0.7.3/download","version":"0.7.3"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"security-framework","notice_origins":[{"origin":"crate:security-framework@3.7.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:security-framework@3.7.0/LICENSE-MIT","sha256":"91e934255ba3b2f21103d68c5581c23ef34aa95c4628e4405b8c901935e11c69"}],"notices":["91e934255ba3b2f21103d68c5581c23ef34aa95c4628e4405b8c901935e11c69","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/security-framework/3.7.0/download","version":"3.7.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"security-framework-sys","notice_origins":[{"origin":"crate:security-framework-sys@2.17.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:security-framework-sys@2.17.0/LICENSE-MIT","sha256":"91e934255ba3b2f21103d68c5581c23ef34aa95c4628e4405b8c901935e11c69"}],"notices":["91e934255ba3b2f21103d68c5581c23ef34aa95c4628e4405b8c901935e11c69","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/security-framework-sys/2.17.0/download","version":"2.17.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"semver","notice_origins":[{"origin":"crate:semver@1.0.28/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:semver@1.0.28/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/semver/1.0.28/download","version":"1.0.28"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"serde","notice_origins":[{"origin":"crate:serde@1.0.229/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:serde@1.0.229/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/serde/1.0.229/download","version":"1.0.229"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"serde_core","notice_origins":[{"origin":"crate:serde_core@1.0.229/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:serde_core@1.0.229/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/serde_core/1.0.229/download","version":"1.0.229"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"serde_derive","notice_origins":[{"origin":"crate:serde_derive@1.0.229/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:serde_derive@1.0.229/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/serde_derive/1.0.229/download","version":"1.0.229"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"serde_json","notice_origins":[{"origin":"crate:serde_json@1.0.151/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:serde_json@1.0.151/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/serde_json/1.0.151/download","version":"1.0.151"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"serde_spanned","notice_origins":[{"origin":"crate:serde_spanned@1.1.1/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:serde_spanned@1.1.1/LICENSE-MIT","sha256":"6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6"}],"notices":["6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/serde_spanned/1.1.1/download","version":"1.1.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"sha1","notice_origins":[{"origin":"crate:sha1@0.10.7/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:sha1@0.10.7/LICENSE-MIT","sha256":"b4eb00df6e2a4d22518fcaa6a2b4646f249b3a3c9814509b22bd2091f1392ff1"}],"notices":["a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5","b4eb00df6e2a4d22518fcaa6a2b4646f249b3a3c9814509b22bd2091f1392ff1"],"source_url":"https://crates.io/api/v1/crates/sha1/0.10.7/download","version":"0.10.7"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"shlex","notice_origins":[{"origin":"crate:shlex@1.3.0/LICENSE-APACHE","sha256":"553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583"},{"origin":"crate:shlex@1.3.0/LICENSE-MIT","sha256":"4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1"}],"notices":["4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1","553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583"],"source_url":"https://crates.io/api/v1/crates/shlex/1.3.0/download","version":"1.3.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"shlex","notice_origins":[{"origin":"crate:shlex@2.0.1/LICENSE-APACHE","sha256":"553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583"},{"origin":"crate:shlex@2.0.1/LICENSE-MIT","sha256":"4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1"}],"notices":["4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1","553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583"],"source_url":"https://crates.io/api/v1/crates/shlex/2.0.1/download","version":"2.0.1"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"signature","notice_origins":[{"origin":"crate:signature@2.2.0/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:signature@2.2.0/LICENSE-MIT","sha256":"b3470648aff02beb36d7a53240fc9260ed80ed93bd43bace6b67d7ef7336ee33"}],"notices":["a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5","b3470648aff02beb36d7a53240fc9260ed80ed93bd43bace6b67d7ef7336ee33"],"source_url":"https://crates.io/api/v1/crates/signature/2.2.0/download","version":"2.2.0"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"simd_cesu8","notice_origins":[{"origin":"crate:simd_cesu8@1.2.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:simd_cesu8@1.2.0/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/simd_cesu8/1.2.0/download","version":"1.2.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"simdutf8","notice_origins":[{"origin":"crate:simdutf8@0.1.5/LICENSE-Apache","sha256":"0cec06e0e55fbc3dc5cee4fca9b607f66cb8f4e4dbcf3b3c013594dd156732e9"},{"origin":"crate:simdutf8@0.1.5/LICENSE-MIT","sha256":"1847e0e0698142ed4347c1441a9fa81c8fbddd44b1d8bbcd5e3647f991759d7f"}],"notices":["0cec06e0e55fbc3dc5cee4fca9b607f66cb8f4e4dbcf3b3c013594dd156732e9","1847e0e0698142ed4347c1441a9fa81c8fbddd44b1d8bbcd5e3647f991759d7f"],"source_url":"https://crates.io/api/v1/crates/simdutf8/0.1.5/download","version":"0.1.5"},{"ecosystem":"cargo","license_expression":"MIT","name":"slab","notice_origins":[{"origin":"crate:slab@0.4.12/LICENSE","sha256":"8ce0830173fdac609dfb4ea603fdc002c2f4af0dc9b1a005653f5da9cf534b18"}],"notices":["8ce0830173fdac609dfb4ea603fdc002c2f4af0dc9b1a005653f5da9cf534b18"],"source_url":"https://crates.io/api/v1/crates/slab/0.4.12/download","version":"0.4.12"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"smallvec","notice_origins":[{"origin":"crate:smallvec@1.16.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:smallvec@1.16.0/LICENSE-MIT","sha256":"0b28172679e0009b655da42797c03fd163a3379d5cfa67ba1f1655e974a2a1a9"}],"notices":["0b28172679e0009b655da42797c03fd163a3379d5cfa67ba1f1655e974a2a1a9","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/smallvec/1.16.0/download","version":"1.16.0"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"spki","notice_origins":[{"origin":"crate:spki@0.7.3/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:spki@0.7.3/LICENSE-MIT","sha256":"c995204cc6bad2ed67dd41f7d89bb9f1a9d48e0edd745732b30640d7912089a4"}],"notices":["a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5","c995204cc6bad2ed67dd41f7d89bb9f1a9d48e0edd745732b30640d7912089a4"],"source_url":"https://crates.io/api/v1/crates/spki/0.7.3/download","version":"0.7.3"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"stable_deref_trait","notice_origins":[{"origin":"crate:stable_deref_trait@1.2.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:stable_deref_trait@1.2.1/LICENSE-MIT","sha256":"5e05b024f653a5ce199e77cbbbd42fb5553562ec714b819421ed0c3e552a75d7"}],"notices":["5e05b024f653a5ce199e77cbbbd42fb5553562ec714b819421ed0c3e552a75d7","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/stable_deref_trait/1.2.1/download","version":"1.2.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"str0m","notice_origins":[{"origin":"crate:str0m@0.20.0/LICENSE-MIT.txt","sha256":"5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b"},{"origin":"crate:str0m@0.20.0/src/packet/LICENSE-APACHE.txt","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"}],"notices":["5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/str0m/0.20.0/download","version":"0.20.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"str0m-aws-lc-rs","notice_origins":[{"origin":"https://raw.githubusercontent.com/algesten/str0m/dbf9fa003bc6da1fc19cdda56a76bd7d48e7b18f/LICENSE-MIT.txt","sha256":"5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b"}],"notices":["5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b"],"source_url":"https://crates.io/api/v1/crates/str0m-aws-lc-rs/0.4.1/download","version":"0.4.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"str0m-proto","notice_origins":[{"origin":"https://raw.githubusercontent.com/algesten/str0m/dbf9fa003bc6da1fc19cdda56a76bd7d48e7b18f/LICENSE-MIT.txt","sha256":"5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b"}],"notices":["5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b"],"source_url":"https://crates.io/api/v1/crates/str0m-proto/0.5.1/download","version":"0.5.1"},{"ecosystem":"cargo","license_expression":"BSD-3-Clause","name":"subtle","notice_origins":[{"origin":"crate:subtle@2.6.1/LICENSE","sha256":"d1fc1bc0d155df60b2e7705b6b2ae02a05c96f948e1cec6e2fb86360b09f346b"}],"notices":["d1fc1bc0d155df60b2e7705b6b2ae02a05c96f948e1cec6e2fb86360b09f346b"],"source_url":"https://crates.io/api/v1/crates/subtle/2.6.1/download","version":"2.6.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"syn","notice_origins":[{"origin":"crate:syn@2.0.119/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:syn@2.0.119/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/syn/2.0.119/download","version":"2.0.119"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"syn","notice_origins":[{"origin":"crate:syn@3.0.4/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:syn@3.0.4/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/syn/3.0.4/download","version":"3.0.4"},{"ecosystem":"cargo","license_expression":"MIT","name":"synstructure","notice_origins":[{"origin":"crate:synstructure@0.13.2/LICENSE","sha256":"219920e865eee70b7dcfc948a86b099e7f4fe2de01bcca2ca9a20c0a033f2b59"}],"notices":["219920e865eee70b7dcfc948a86b099e7f4fe2de01bcca2ca9a20c0a033f2b59"],"source_url":"https://crates.io/api/v1/crates/synstructure/0.13.2/download","version":"0.13.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"system-deps","notice_origins":[{"origin":"crate:system-deps@7.0.8/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:system-deps@7.0.8/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/system-deps/7.0.8/download","version":"7.0.8"},{"ecosystem":"cargo","license_expression":"Apache-2.0 WITH LLVM-exception","name":"target-lexicon","notice_origins":[{"origin":"crate:target-lexicon@0.13.5/LICENSE","sha256":"268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5"}],"notices":["268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5"],"source_url":"https://crates.io/api/v1/crates/target-lexicon/0.13.5/download","version":"0.13.5"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"tempfile","notice_origins":[{"origin":"crate:tempfile@3.27.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:tempfile@3.27.0/LICENSE-MIT","sha256":"8b427f5bc501764575e52ba4f9d95673cf8f6d80a86d0d06599852e1a9a20a36"}],"notices":["8b427f5bc501764575e52ba4f9d95673cf8f6d80a86d0d06599852e1a9a20a36","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/tempfile/3.27.0/download","version":"3.27.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"thiserror","notice_origins":[{"origin":"crate:thiserror@1.0.69/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:thiserror@1.0.69/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/thiserror/1.0.69/download","version":"1.0.69"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"thiserror","notice_origins":[{"origin":"crate:thiserror@2.0.20/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:thiserror@2.0.20/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/thiserror/2.0.20/download","version":"2.0.20"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"thiserror-impl","notice_origins":[{"origin":"crate:thiserror-impl@1.0.69/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:thiserror-impl@1.0.69/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/thiserror-impl/1.0.69/download","version":"1.0.69"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"thiserror-impl","notice_origins":[{"origin":"crate:thiserror-impl@2.0.20/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:thiserror-impl@2.0.20/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/thiserror-impl/2.0.20/download","version":"2.0.20"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"time","notice_origins":[{"origin":"crate:time@0.3.55/LICENSE-Apache","sha256":"0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594"},{"origin":"crate:time@0.3.55/LICENSE-MIT","sha256":"2537228d9a1b44a5dc595241349cae7090b326c8de165aaf89bfddef4a00d0fc"}],"notices":["0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594","2537228d9a1b44a5dc595241349cae7090b326c8de165aaf89bfddef4a00d0fc"],"source_url":"https://crates.io/api/v1/crates/time/0.3.55/download","version":"0.3.55"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"time-core","notice_origins":[{"origin":"crate:time-core@0.1.9/LICENSE-Apache","sha256":"0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594"},{"origin":"crate:time-core@0.1.9/LICENSE-MIT","sha256":"2537228d9a1b44a5dc595241349cae7090b326c8de165aaf89bfddef4a00d0fc"}],"notices":["0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594","2537228d9a1b44a5dc595241349cae7090b326c8de165aaf89bfddef4a00d0fc"],"source_url":"https://crates.io/api/v1/crates/time-core/0.1.9/download","version":"0.1.9"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"time-macros","notice_origins":[{"origin":"crate:time-macros@0.2.32/LICENSE-Apache","sha256":"0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594"},{"origin":"crate:time-macros@0.2.32/LICENSE-MIT","sha256":"2537228d9a1b44a5dc595241349cae7090b326c8de165aaf89bfddef4a00d0fc"}],"notices":["0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594","2537228d9a1b44a5dc595241349cae7090b326c8de165aaf89bfddef4a00d0fc"],"source_url":"https://crates.io/api/v1/crates/time-macros/0.2.32/download","version":"0.2.32"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"tinystr","notice_origins":[{"origin":"crate:tinystr@0.8.4/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/tinystr/0.8.4/download","version":"0.8.4"},{"ecosystem":"cargo","license_expression":"MIT","name":"tokio","notice_origins":[{"origin":"crate:tokio@1.53.1/LICENSE","sha256":"253cd04c6714889df2d32f3f64d669179a1c95c76ac43c40882c52eb06bc3552"}],"notices":["253cd04c6714889df2d32f3f64d669179a1c95c76ac43c40882c52eb06bc3552"],"source_url":"https://crates.io/api/v1/crates/tokio/1.53.1/download","version":"1.53.1"},{"ecosystem":"cargo","license_expression":"MIT","name":"tokio-macros","notice_origins":[{"origin":"crate:tokio-macros@2.7.2/LICENSE","sha256":"0b83dc40cba89b9922bb84b0a9c7d2768ce37c1d7e138b7424fd4549915778c9"}],"notices":["0b83dc40cba89b9922bb84b0a9c7d2768ce37c1d7e138b7424fd4549915778c9"],"source_url":"https://crates.io/api/v1/crates/tokio-macros/2.7.2/download","version":"2.7.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"toml","notice_origins":[{"origin":"crate:toml@1.1.5+spec-1.1.0/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:toml@1.1.5+spec-1.1.0/LICENSE-MIT","sha256":"6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6"}],"notices":["6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/toml/1.1.5+spec-1.1.0/download","version":"1.1.5+spec-1.1.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"toml_datetime","notice_origins":[{"origin":"crate:toml_datetime@1.1.1+spec-1.1.0/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:toml_datetime@1.1.1+spec-1.1.0/LICENSE-MIT","sha256":"6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6"}],"notices":["6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/toml_datetime/1.1.1+spec-1.1.0/download","version":"1.1.1+spec-1.1.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"toml_edit","notice_origins":[{"origin":"crate:toml_edit@0.25.13+spec-1.1.0/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:toml_edit@0.25.13+spec-1.1.0/LICENSE-MIT","sha256":"6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6"}],"notices":["6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/toml_edit/0.25.13+spec-1.1.0/download","version":"0.25.13+spec-1.1.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"toml_parser","notice_origins":[{"origin":"crate:toml_parser@1.1.3+spec-1.1.0/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:toml_parser@1.1.3+spec-1.1.0/LICENSE-MIT","sha256":"6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6"}],"notices":["6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/toml_parser/1.1.3+spec-1.1.0/download","version":"1.1.3+spec-1.1.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"toml_writer","notice_origins":[{"origin":"crate:toml_writer@1.1.2+spec-1.1.0/LICENSE-APACHE","sha256":"c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"},{"origin":"crate:toml_writer@1.1.2+spec-1.1.0/LICENSE-MIT","sha256":"6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6"}],"notices":["6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6","c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08"],"source_url":"https://crates.io/api/v1/crates/toml_writer/1.1.2+spec-1.1.0/download","version":"1.1.2+spec-1.1.0"},{"ecosystem":"cargo","license_expression":"MIT","name":"tracing","notice_origins":[{"origin":"crate:tracing@0.1.44/LICENSE","sha256":"898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1"}],"notices":["898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1"],"source_url":"https://crates.io/api/v1/crates/tracing/0.1.44/download","version":"0.1.44"},{"ecosystem":"cargo","license_expression":"MIT","name":"tracing-attributes","notice_origins":[{"origin":"crate:tracing-attributes@0.1.31/LICENSE","sha256":"898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1"}],"notices":["898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1"],"source_url":"https://crates.io/api/v1/crates/tracing-attributes/0.1.31/download","version":"0.1.31"},{"ecosystem":"cargo","license_expression":"MIT","name":"tracing-core","notice_origins":[{"origin":"crate:tracing-core@0.1.36/LICENSE","sha256":"898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1"},{"origin":"crate:tracing-core@0.1.36/src/spin/LICENSE","sha256":"58545fed1565e42d687aecec6897d35c6d37ccb71479a137c0deb2203e125c79"}],"notices":["58545fed1565e42d687aecec6897d35c6d37ccb71479a137c0deb2203e125c79","898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1"],"source_url":"https://crates.io/api/v1/crates/tracing-core/0.1.36/download","version":"0.1.36"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"tungstenite","notice_origins":[{"origin":"crate:tungstenite@0.29.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:tungstenite@0.29.0/LICENSE-MIT","sha256":"7fea0ee51a4ca5d5cea7464135fd55e8b09caf3a61da3d451ac8a22af95c033f"}],"notices":["7fea0ee51a4ca5d5cea7464135fd55e8b09caf3a61da3d451ac8a22af95c033f","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/tungstenite/0.29.0/download","version":"0.29.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"typenum","notice_origins":[{"origin":"crate:typenum@1.20.1/LICENSE","sha256":"db11fec9946737df39ca3898d9cd8c10ec6f6c3a884a6802b0ad0b81b4e8f23a"},{"origin":"crate:typenum@1.20.1/LICENSE-APACHE","sha256":"516b24e051bf5630880ebbd55c40a25ce9552ebaf8970a53e8976eb70e522406"},{"origin":"crate:typenum@1.20.1/LICENSE-MIT","sha256":"a825bd853ab71619a4923d7b4311221427848070ff44d990da39b0b274c1683f"}],"notices":["516b24e051bf5630880ebbd55c40a25ce9552ebaf8970a53e8976eb70e522406","a825bd853ab71619a4923d7b4311221427848070ff44d990da39b0b274c1683f","db11fec9946737df39ca3898d9cd8c10ec6f6c3a884a6802b0ad0b81b4e8f23a"],"source_url":"https://crates.io/api/v1/crates/typenum/1.20.1/download","version":"1.20.1"},{"ecosystem":"cargo","license_expression":"(MIT OR Apache-2.0) AND Unicode-3.0","name":"unicode-ident","notice_origins":[{"origin":"crate:unicode-ident@1.0.24/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:unicode-ident@1.0.24/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"},{"origin":"crate:unicode-ident@1.0.24/LICENSE-UNICODE","sha256":"f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a","f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1"],"source_url":"https://crates.io/api/v1/crates/unicode-ident/1.0.24/download","version":"1.0.24"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"unicode-width","notice_origins":[{"origin":"crate:unicode-width@0.2.2/COPYRIGHT","sha256":"23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d"},{"origin":"crate:unicode-width@0.2.2/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:unicode-width@0.2.2/LICENSE-MIT","sha256":"7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0"}],"notices":["23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d","7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/unicode-width/0.2.2/download","version":"0.2.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"unindent","notice_origins":[{"origin":"crate:unindent@0.2.4/LICENSE-APACHE","sha256":"62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"},{"origin":"crate:unindent@0.2.4/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a"],"source_url":"https://crates.io/api/v1/crates/unindent/0.2.4/download","version":"0.2.4"},{"ecosystem":"cargo","license_expression":"ISC","name":"untrusted","notice_origins":[{"origin":"crate:untrusted@0.7.1/LICENSE.txt","sha256":"7abd9b6960dcf7d4d0a48606a5b71bfe37d472db68d70637f3a58a56785f1621"}],"notices":["7abd9b6960dcf7d4d0a48606a5b71bfe37d472db68d70637f3a58a56785f1621"],"source_url":"https://crates.io/api/v1/crates/untrusted/0.7.1/download","version":"0.7.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"url","notice_origins":[{"origin":"crate:url@2.5.8/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:url@2.5.8/LICENSE-MIT","sha256":"b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5"}],"notices":["a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2","b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5"],"source_url":"https://crates.io/api/v1/crates/url/2.5.8/download","version":"2.5.8"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"utf8_iter","notice_origins":[{"origin":"crate:utf8_iter@1.0.4/COPYRIGHT","sha256":"c30152c94a6d75e021adbc52b3a52470366a46edb917e17deae3259251af244c"},{"origin":"crate:utf8_iter@1.0.4/LICENSE-APACHE","sha256":"cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"},{"origin":"crate:utf8_iter@1.0.4/LICENSE-MIT","sha256":"3fa4ca83dcc9237839b1bdeb2e6d16bdfb5ec0c5ce42b24694d8bbf0dcbef72c"}],"notices":["3fa4ca83dcc9237839b1bdeb2e6d16bdfb5ec0c5ce42b24694d8bbf0dcbef72c","c30152c94a6d75e021adbc52b3a52470366a46edb917e17deae3259251af244c","cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"],"source_url":"https://crates.io/api/v1/crates/utf8_iter/1.0.4/download","version":"1.0.4"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"vcpkg","notice_origins":[{"origin":"crate:vcpkg@0.2.15/LICENSE-APACHE","sha256":"60c93a31f490375aadf64098b75f10715010379541021e00261045d7800611d3"},{"origin":"crate:vcpkg@0.2.15/LICENSE-MIT","sha256":"016d20f335060a70e79d9fcf8dfaa6201114d65d592211f4bdfb8ae9ca2bc1dc"}],"notices":["016d20f335060a70e79d9fcf8dfaa6201114d65d592211f4bdfb8ae9ca2bc1dc","60c93a31f490375aadf64098b75f10715010379541021e00261045d7800611d3"],"source_url":"https://crates.io/api/v1/crates/vcpkg/0.2.15/download","version":"0.2.15"},{"ecosystem":"cargo","license_expression":"MIT","name":"version-compare","notice_origins":[{"origin":"crate:version-compare@0.2.1/LICENSE","sha256":"cedfcc7ace1639adb054bd4a19b6f8585ccb2429a60b4bf51bfeb0601058c22c"}],"notices":["cedfcc7ace1639adb054bd4a19b6f8585ccb2429a60b4bf51bfeb0601058c22c"],"source_url":"https://crates.io/api/v1/crates/version-compare/0.2.1/download","version":"0.2.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"version_check","notice_origins":[{"origin":"crate:version_check@0.9.5/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:version_check@0.9.5/LICENSE-MIT","sha256":"b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e"}],"notices":["a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2","b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e"],"source_url":"https://crates.io/api/v1/crates/version_check/0.9.5/download","version":"0.9.5"},{"ecosystem":"cargo","license_expression":"Unlicense OR MIT","name":"walkdir","notice_origins":[{"origin":"crate:walkdir@2.5.0/COPYING","sha256":"01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f"},{"origin":"crate:walkdir@2.5.0/LICENSE-MIT","sha256":"0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f"}],"notices":["01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f","0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f"],"source_url":"https://crates.io/api/v1/crates/walkdir/2.5.0/download","version":"2.5.0"},{"ecosystem":"cargo","license_expression":"MIT","name":"wasapi","notice_origins":[{"origin":"crate:wasapi@0.23.0/LICENSE.txt","sha256":"55c8990ea1221b3f21cb1e603e97f8ea268cc8db082999ed59e39fc43d45fedf"}],"notices":["55c8990ea1221b3f21cb1e603e97f8ea268cc8db082999ed59e39fc43d45fedf"],"source_url":"https://crates.io/api/v1/crates/wasapi/0.23.0/download","version":"0.23.0"},{"ecosystem":"cargo","license_expression":"Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT","name":"wasip2","notice_origins":[{"origin":"crate:wasip2@1.0.4+wasi-0.2.12/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:wasip2@1.0.4+wasi-0.2.12/LICENSE-Apache-2.0_WITH_LLVM-exception","sha256":"268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5"},{"origin":"crate:wasip2@1.0.4+wasi-0.2.12/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/wasip2/1.0.4+wasi-0.2.12/download","version":"1.0.4+wasi-0.2.12"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"wasm-bindgen","notice_origins":[{"origin":"crate:wasm-bindgen@0.2.127/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:wasm-bindgen@0.2.127/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/wasm-bindgen/0.2.127/download","version":"0.2.127"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"wasm-bindgen-macro","notice_origins":[{"origin":"crate:wasm-bindgen-macro@0.2.127/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:wasm-bindgen-macro@0.2.127/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/wasm-bindgen-macro/0.2.127/download","version":"0.2.127"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"wasm-bindgen-macro-support","notice_origins":[{"origin":"crate:wasm-bindgen-macro-support@0.2.127/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:wasm-bindgen-macro-support@0.2.127/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/wasm-bindgen-macro-support/0.2.127/download","version":"0.2.127"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"wasm-bindgen-shared","notice_origins":[{"origin":"crate:wasm-bindgen-shared@0.2.127/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:wasm-bindgen-shared@0.2.127/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/wasm-bindgen-shared/0.2.127/download","version":"0.2.127"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"web-sys","notice_origins":[{"origin":"crate:web-sys@0.3.104/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:web-sys@0.3.104/LICENSE-MIT","sha256":"378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397"}],"notices":["378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/web-sys/0.3.104/download","version":"0.3.104"},{"ecosystem":"cargo","license_expression":"BSD-3-Clause","name":"webrtc-audio-processing","notice_origins":[{"origin":"crate:webrtc-audio-processing@2.1.0/COPYING","sha256":"6db9d4840c6ff0fb3c37ace8e32cfd3eb6c6e759c67b4ecbee969cd8d75154a9"}],"notices":["6db9d4840c6ff0fb3c37ace8e32cfd3eb6c6e759c67b4ecbee969cd8d75154a9"],"source_url":"https://crates.io/crates/webrtc-audio-processing/2.1.0","version":"2.1.0"},{"ecosystem":"cargo","license_expression":"BSD-3-Clause","name":"webrtc-audio-processing-config","notice_origins":[{"origin":"crate:webrtc-audio-processing-config@2.1.0/COPYING","sha256":"9b79539028e216e813e152d45f5c1ed5fdd0554426ad50270fb03134e7082dac"}],"notices":["9b79539028e216e813e152d45f5c1ed5fdd0554426ad50270fb03134e7082dac"],"source_url":"https://crates.io/crates/webrtc-audio-processing-config/2.1.0","version":"2.1.0"},{"ecosystem":"cargo","license_expression":"BSD-3-Clause AND Apache-2.0 AND LicenseRef-WebRTC-Bundled","name":"webrtc-audio-processing-sys","notice_origins":[{"origin":"crate:webrtc-audio-processing-sys@2.1.0/COPYING","sha256":"9b79539028e216e813e152d45f5c1ed5fdd0554426ad50270fb03134e7082dac"},{"origin":"crate:webrtc-audio-processing-sys@2.1.0/webrtc-audio-processing/COPYING","sha256":"9b79539028e216e813e152d45f5c1ed5fdd0554426ad50270fb03134e7082dac"},{"origin":"crate:webrtc-audio-processing-sys@2.1.0/webrtc-audio-processing/webrtc/LICENSE","sha256":"ab00a482b6a3902e40211b43c5d0441962ea99b6cc7c25c0f243fa270b78d482"},{"origin":"crate:webrtc-audio-processing-sys@2.1.0/webrtc-audio-processing/webrtc/PATENTS","sha256":"01462e2068d1a04c2274f3389773014c14ed9bc3446b28303543bd3e3c064145"},{"origin":"crate:webrtc-audio-processing-sys@2.1.0/webrtc-audio-processing/webrtc/common_audio/third_party/ooura/LICENSE","sha256":"25b7731b70c77ecd5f3bb19303fbaa99be18860f81d44f71da670fdcd04829db"},{"origin":"crate:webrtc-audio-processing-sys@2.1.0/webrtc-audio-processing/webrtc/common_audio/third_party/spl_sqrt_floor/LICENSE","sha256":"41d791701e3e1c1073470403de7e342442d1e6a2af72681023b13a2f45f2125c"},{"origin":"crate:webrtc-audio-processing-sys@2.1.0/webrtc-audio-processing/webrtc/third_party/pffft/LICENSE","sha256":"a46200592eb193853527250da098e6bb0c75424e7a2c7db8da526c4f301c3d88"},{"origin":"crate:webrtc-audio-processing-sys@2.1.0/webrtc-audio-processing/webrtc/third_party/rnnoise/COPYING","sha256":"e2f59ff41d9d03adc3dcf3deff170f8c8cf4a6eb4a9b174762a7656d23200ffa"},{"origin":"crate:webrtc-audio-processing-sys@2.1.0/webrtc-audio-processing/webrtc/modules/third_party/fft/LICENSE","sha256":"6fdbabd2c95c5efc6f1e46175278239afb9343120a3022ed0e0cb04267a6aeb3"},{"origin":"https://github.com/abseil/abseil-cpp/archive/refs/tags/20240722.0.tar.gz#LICENSE","sha256":"c79a7fea0e3cac04cd43f20e7b648e5a0ff8fa5344e644b0ee09ca1162b62747"}],"notices":["01462e2068d1a04c2274f3389773014c14ed9bc3446b28303543bd3e3c064145","25b7731b70c77ecd5f3bb19303fbaa99be18860f81d44f71da670fdcd04829db","41d791701e3e1c1073470403de7e342442d1e6a2af72681023b13a2f45f2125c","6fdbabd2c95c5efc6f1e46175278239afb9343120a3022ed0e0cb04267a6aeb3","9b79539028e216e813e152d45f5c1ed5fdd0554426ad50270fb03134e7082dac","a46200592eb193853527250da098e6bb0c75424e7a2c7db8da526c4f301c3d88","ab00a482b6a3902e40211b43c5d0441962ea99b6cc7c25c0f243fa270b78d482","c79a7fea0e3cac04cd43f20e7b648e5a0ff8fa5344e644b0ee09ca1162b62747","e2f59ff41d9d03adc3dcf3deff170f8c8cf4a6eb4a9b174762a7656d23200ffa"],"source_url":"https://crates.io/crates/webrtc-audio-processing-sys/2.1.0","version":"2.1.0"},{"ecosystem":"cargo","license_expression":"Unlicense OR MIT","name":"winapi-util","notice_origins":[{"origin":"crate:winapi-util@0.1.11/COPYING","sha256":"01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f"},{"origin":"crate:winapi-util@0.1.11/LICENSE-MIT","sha256":"cb3c929a05e6cbc9de9ab06a4c57eeb60ca8c724bef6c138c87d3a577e27aa14"}],"notices":["01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f","cb3c929a05e6cbc9de9ab06a4c57eeb60ca8c724bef6c138c87d3a577e27aa14"],"source_url":"https://crates.io/api/v1/crates/winapi-util/0.1.11/download","version":"0.1.11"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows","notice_origins":[{"origin":"crate:windows@0.58.0/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows@0.58.0/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows/0.58.0/download","version":"0.58.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows","notice_origins":[{"origin":"crate:windows@0.62.2/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows@0.62.2/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows/0.62.2/download","version":"0.62.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-collections","notice_origins":[{"origin":"crate:windows-collections@0.3.2/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-collections@0.3.2/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-collections/0.3.2/download","version":"0.3.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-core","notice_origins":[{"origin":"crate:windows-core@0.58.0/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-core@0.58.0/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-core/0.58.0/download","version":"0.58.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-core","notice_origins":[{"origin":"crate:windows-core@0.62.2/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-core@0.62.2/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-core/0.62.2/download","version":"0.62.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-future","notice_origins":[{"origin":"crate:windows-future@0.3.2/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-future@0.3.2/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-future/0.3.2/download","version":"0.3.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-implement","notice_origins":[{"origin":"crate:windows-implement@0.58.0/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-implement@0.58.0/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-implement/0.58.0/download","version":"0.58.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-implement","notice_origins":[{"origin":"crate:windows-implement@0.60.2/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-implement@0.60.2/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-implement/0.60.2/download","version":"0.60.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-interface","notice_origins":[{"origin":"crate:windows-interface@0.58.0/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-interface@0.58.0/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-interface/0.58.0/download","version":"0.58.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-interface","notice_origins":[{"origin":"crate:windows-interface@0.59.3/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-interface@0.59.3/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-interface/0.59.3/download","version":"0.59.3"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-link","notice_origins":[{"origin":"crate:windows-link@0.2.1/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-link@0.2.1/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-link/0.2.1/download","version":"0.2.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-numerics","notice_origins":[{"origin":"crate:windows-numerics@0.3.1/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-numerics@0.3.1/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-numerics/0.3.1/download","version":"0.3.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-result","notice_origins":[{"origin":"crate:windows-result@0.2.0/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-result@0.2.0/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-result/0.2.0/download","version":"0.2.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-result","notice_origins":[{"origin":"crate:windows-result@0.4.1/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-result@0.4.1/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-result/0.4.1/download","version":"0.4.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-strings","notice_origins":[{"origin":"crate:windows-strings@0.1.0/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-strings@0.1.0/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-strings/0.1.0/download","version":"0.1.0"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-strings","notice_origins":[{"origin":"crate:windows-strings@0.5.1/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-strings@0.5.1/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-strings/0.5.1/download","version":"0.5.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-sys","notice_origins":[{"origin":"crate:windows-sys@0.61.2/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-sys@0.61.2/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-sys/0.61.2/download","version":"0.61.2"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-targets","notice_origins":[{"origin":"crate:windows-targets@0.52.6/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-targets@0.52.6/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-targets/0.52.6/download","version":"0.52.6"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows-threading","notice_origins":[{"origin":"crate:windows-threading@0.2.1/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows-threading@0.2.1/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows-threading/0.2.1/download","version":"0.2.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows_aarch64_gnullvm","notice_origins":[{"origin":"crate:windows_aarch64_gnullvm@0.52.6/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows_aarch64_gnullvm@0.52.6/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows_aarch64_gnullvm/0.52.6/download","version":"0.52.6"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows_aarch64_msvc","notice_origins":[{"origin":"crate:windows_aarch64_msvc@0.52.6/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows_aarch64_msvc@0.52.6/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows_aarch64_msvc/0.52.6/download","version":"0.52.6"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows_i686_gnu","notice_origins":[{"origin":"crate:windows_i686_gnu@0.52.6/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows_i686_gnu@0.52.6/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows_i686_gnu/0.52.6/download","version":"0.52.6"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows_i686_gnullvm","notice_origins":[{"origin":"crate:windows_i686_gnullvm@0.52.6/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows_i686_gnullvm@0.52.6/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows_i686_gnullvm/0.52.6/download","version":"0.52.6"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows_i686_msvc","notice_origins":[{"origin":"crate:windows_i686_msvc@0.52.6/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows_i686_msvc@0.52.6/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows_i686_msvc/0.52.6/download","version":"0.52.6"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows_x86_64_gnu","notice_origins":[{"origin":"crate:windows_x86_64_gnu@0.52.6/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows_x86_64_gnu@0.52.6/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows_x86_64_gnu/0.52.6/download","version":"0.52.6"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows_x86_64_gnullvm","notice_origins":[{"origin":"crate:windows_x86_64_gnullvm@0.52.6/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows_x86_64_gnullvm@0.52.6/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows_x86_64_gnullvm/0.52.6/download","version":"0.52.6"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"windows_x86_64_msvc","notice_origins":[{"origin":"crate:windows_x86_64_msvc@0.52.6/license-apache-2.0","sha256":"c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b"},{"origin":"crate:windows_x86_64_msvc@0.52.6/license-mit","sha256":"c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"}],"notices":["c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b","c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383"],"source_url":"https://crates.io/api/v1/crates/windows_x86_64_msvc/0.52.6/download","version":"0.52.6"},{"ecosystem":"cargo","license_expression":"MIT","name":"winnow","notice_origins":[{"origin":"crate:winnow@1.0.4/LICENSE-MIT","sha256":"cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d"}],"notices":["cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d"],"source_url":"https://crates.io/api/v1/crates/winnow/1.0.4/download","version":"1.0.4"},{"ecosystem":"cargo","license_expression":"Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT","name":"wit-bindgen","notice_origins":[{"origin":"crate:wit-bindgen@0.57.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:wit-bindgen@0.57.1/LICENSE-Apache-2.0_WITH_LLVM-exception","sha256":"268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5"},{"origin":"crate:wit-bindgen@0.57.1/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3","268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/wit-bindgen/0.57.1/download","version":"0.57.1"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"writeable","notice_origins":[{"origin":"crate:writeable@0.6.4/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/writeable/0.6.4/download","version":"0.6.4"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"x509-cert","notice_origins":[{"origin":"crate:x509-cert@0.2.5/LICENSE-APACHE","sha256":"a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"},{"origin":"crate:x509-cert@0.2.5/LICENSE-MIT","sha256":"90c503b61dee04e1449c323ec34c229dfb68d7adcb96c7e140ee55f70fce2d8e"}],"notices":["90c503b61dee04e1449c323ec34c229dfb68d7adcb96c7e140ee55f70fce2d8e","a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5"],"source_url":"https://crates.io/api/v1/crates/x509-cert/0.2.5/download","version":"0.2.5"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"x509-parser","notice_origins":[{"origin":"crate:x509-parser@0.18.1/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:x509-parser@0.18.1/LICENSE-MIT","sha256":"a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513"}],"notices":["a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/x509-parser/0.18.1/download","version":"0.18.1"},{"ecosystem":"cargo","license_expression":"MIT OR Apache-2.0","name":"yasna","notice_origins":[{"origin":"crate:yasna@0.6.0/LICENSE-APACHE","sha256":"a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"},{"origin":"crate:yasna@0.6.0/LICENSE-MIT","sha256":"2a7df90e60fd5512b8bca35d3ce90e068f21c52d962855053fd1d9e2e7ca0f16"}],"notices":["2a7df90e60fd5512b8bca35d3ce90e068f21c52d962855053fd1d9e2e7ca0f16","a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2"],"source_url":"https://crates.io/api/v1/crates/yasna/0.6.0/download","version":"0.6.0"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"yoke","notice_origins":[{"origin":"crate:yoke@0.8.3/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/yoke/0.8.3/download","version":"0.8.3"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"yoke-derive","notice_origins":[{"origin":"crate:yoke-derive@0.8.2/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/yoke-derive/0.8.2/download","version":"0.8.2"},{"ecosystem":"cargo","license_expression":"BSD-2-Clause OR Apache-2.0 OR MIT","name":"zerocopy","notice_origins":[{"origin":"crate:zerocopy@0.8.56/LICENSE-APACHE","sha256":"9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3"},{"origin":"crate:zerocopy@0.8.56/LICENSE-BSD","sha256":"83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32"},{"origin":"crate:zerocopy@0.8.56/LICENSE-MIT","sha256":"1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df"}],"notices":["1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df","83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32","9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3"],"source_url":"https://crates.io/api/v1/crates/zerocopy/0.8.56/download","version":"0.8.56"},{"ecosystem":"cargo","license_expression":"BSD-2-Clause OR Apache-2.0 OR MIT","name":"zerocopy-derive","notice_origins":[{"origin":"crate:zerocopy-derive@0.8.56/LICENSE-APACHE","sha256":"9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3"},{"origin":"crate:zerocopy-derive@0.8.56/LICENSE-BSD","sha256":"83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32"},{"origin":"crate:zerocopy-derive@0.8.56/LICENSE-MIT","sha256":"1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df"}],"notices":["1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df","83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32","9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3"],"source_url":"https://crates.io/api/v1/crates/zerocopy-derive/0.8.56/download","version":"0.8.56"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"zerofrom","notice_origins":[{"origin":"crate:zerofrom@0.1.8/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/zerofrom/0.1.8/download","version":"0.1.8"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"zerofrom-derive","notice_origins":[{"origin":"crate:zerofrom-derive@0.1.7/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/zerofrom-derive/0.1.7/download","version":"0.1.7"},{"ecosystem":"cargo","license_expression":"Apache-2.0 OR MIT","name":"zeroize","notice_origins":[{"origin":"crate:zeroize@1.9.0/LICENSE-APACHE","sha256":"cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"},{"origin":"crate:zeroize@1.9.0/LICENSE-MIT","sha256":"8c7516d4b27b1e495be5e38b612298b63de48d05f49cdac94f70f3cd70f8864b"}],"notices":["8c7516d4b27b1e495be5e38b612298b63de48d05f49cdac94f70f3cd70f8864b","cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"],"source_url":"https://crates.io/api/v1/crates/zeroize/1.9.0/download","version":"1.9.0"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"zerotrie","notice_origins":[{"origin":"crate:zerotrie@0.2.5/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/zerotrie/0.2.5/download","version":"0.2.5"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"zerovec","notice_origins":[{"origin":"crate:zerovec@0.11.8/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/zerovec/0.11.8/download","version":"0.11.8"},{"ecosystem":"cargo","license_expression":"Unicode-3.0","name":"zerovec-derive","notice_origins":[{"origin":"crate:zerovec-derive@0.11.6/LICENSE","sha256":"f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"}],"notices":["f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2"],"source_url":"https://crates.io/api/v1/crates/zerovec-derive/0.11.6/download","version":"0.11.6"},{"ecosystem":"cargo","license_expression":"MIT","name":"zmij","notice_origins":[{"origin":"crate:zmij@1.0.23/LICENSE-MIT","sha256":"23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"}],"notices":["23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3"],"source_url":"https://crates.io/api/v1/crates/zmij/1.0.23/download","version":"1.0.23"},{"ecosystem":"rpm","license_expression":"LGPL-2.1-or-later","name":"alsa-lib","notice_origins":[{"origin":"alsa-lib-1.2.15.3.tar.bz2:alsa-lib-1.2.15.3/COPYING","sha256":"32434afcc8666ba060e111d715bfdb6c2d5dd8a35fa4d3ab8ad67d8f850d2f2b"}],"notices":["32434afcc8666ba060e111d715bfdb6c2d5dd8a35fa4d3ab8ad67d8f850d2f2b"],"source_sha256":"25ed978df0d27df4eba2aee62046b21943d31c2d17a2aacef813a1f115d213b2","source_url":"https://repo.almalinux.org/vault/9.8/AppStream/Source/Packages/alsa-lib-1.2.15.3-1.el9.src.rpm","version":"1.2.15.3-1.el9"},{"ecosystem":"rpm","license_expression":"Apache-2.0","name":"openssl-libs","notice_origins":[{"origin":"openssl-3.5.8.tar.gz:openssl-3.5.8/LICENSE.txt","sha256":"7d5450cb2d142651b8afa315b5f238efc805dad827d91ba367d8516bc9d49e7a"}],"notices":["7d5450cb2d142651b8afa315b5f238efc805dad827d91ba367d8516bc9d49e7a"],"source_sha256":"347ba8e8e6b4483c71aa0082a5ebaf5da57cac0bbfb40d514b93c904ffe79d6b","source_url":"https://repo.almalinux.org/vault/9.8/BaseOS/Source/Packages/openssl-3.5.8-1.el9_8.src.rpm","version":"3.5.8-1.el9_8"},{"ecosystem":"rpm","license_expression":"MIT","name":"pipewire-libs","notice_origins":[{"origin":"pipewire-1.4.11.tar.gz:pipewire-1.4.11/COPYING","sha256":"8909c319a7e27dbb33a15b9035f89ab3b7b2f6a12f8bcddc755206a8db1ada44"},{"origin":"pipewire-1.4.11.tar.gz:pipewire-1.4.11/LICENSE","sha256":"be4be5d77424833edf31f53fc1f1cecb6996b9e2d747d9e6fb8f878362ebc92b"}],"notices":["8909c319a7e27dbb33a15b9035f89ab3b7b2f6a12f8bcddc755206a8db1ada44","be4be5d77424833edf31f53fc1f1cecb6996b9e2d747d9e6fb8f878362ebc92b"],"source_sha256":"2c29324b46766da8da90fcca9eada5a8d2ffb4577f7c00abb9c40ddb9e1f1e91","source_url":"https://repo.almalinux.org/vault/9.8/AppStream/Source/Packages/pipewire-1.4.11-1.el9_8.2.src.rpm","version":"1.4.11-1.el9_8.2"}],"schema_version":1}
-->

## aead 0.5.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/aead/0.5.2/download

Notice SHA-256: `949ab7b3e7140fee216f06fe3a2bd67d68dd511f8ea73c1e01c98cb348e9c8ae`

Notice SHA-256: `b1cf9a3333ca78152b859012cd4a804156e5243e9ca20ad1df7327ba5ea7405c`

## aes 0.8.4

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/aes/0.8.4/download

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

Notice SHA-256: `f7e8ab639afef15573680c97f796166835cbeb3865175882fea41c60d106b733`

## aho-corasick 1.1.5

License: `Unlicense OR MIT`.

Source: https://crates.io/api/v1/crates/aho-corasick/1.1.5/download

Notice SHA-256: `01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f`

Notice SHA-256: `0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f`

## alsa 0.11.0

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/alsa/0.11.0/download

Notice SHA-256: `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594`

Notice SHA-256: `3cc33f8e76680b9cba2e2a5bc94de5a92420045863ab2fadbef290a55b4d8530`

## alsa-sys 0.4.0

License: `MIT`.

Source: https://crates.io/api/v1/crates/alsa-sys/0.4.0/download

Notice SHA-256: `219766b3420f49f6204143c5f3ef750888fb6de29ce5f63e909f146e90b375a2`

## annotate-snippets 0.11.5

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/annotate-snippets/0.11.5/download

Notice SHA-256: `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## anstyle 1.0.14

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/anstyle/1.0.14/download

Notice SHA-256: `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## anyhow 1.0.104

License: `MIT OR Apache-2.0`.

Source: https://crates.io/crates/anyhow/1.0.104

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## arrayvec 0.7.8

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/arrayvec/0.7.8/download

Notice SHA-256: `4da95ec4ecb65b738d470b7d762894ad9c97da93e6cbfb18b570fc2c96f4b871`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## asn1-rs 0.7.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/asn1-rs/0.7.2/download

Notice SHA-256: `a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## asn1-rs-derive 0.6.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/asn1-rs-derive/0.6.0/download

Notice SHA-256: `a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## asn1-rs-impl 0.2.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/asn1-rs-impl/0.2.0/download

Notice SHA-256: `a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## autocfg 1.5.1

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/autocfg/1.5.1/download

Notice SHA-256: `27995d58ad5c1145c1a8cd86244ce844886958a35eb2b78c6b772748669999ac`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## autotools 0.2.7

License: `MIT`.

Source: https://crates.io/crates/autotools/0.2.7

Notice SHA-256: `334c40cc7ab76303a1555e77724200631cf31c2a3846b2602161cf8921210b46`

## aws-lc-rs 1.18.1

License: `ISC AND (Apache-2.0 OR ISC)`.

Source: https://crates.io/api/v1/crates/aws-lc-rs/1.18.1/download

Notice SHA-256: `b50b376e7d24a0598488b730c3034ffcd0b58dd36c0913a24b9903a3cfd04bf7`

## aws-lc-sys 0.45.0

License: `ISC AND (Apache-2.0 OR ISC) AND Apache-2.0 AND MIT AND BSD-3-Clause AND (Apache-2.0 OR ISC OR MIT) AND (Apache-2.0 OR ISC OR MIT-0)`.

Source: https://crates.io/api/v1/crates/aws-lc-sys/0.45.0/download

Notice SHA-256: `43e358d7b6eb109d0f51f7b3a090fd82607965767c25fadee39e922475de2061`

Notice SHA-256: `728536b4160e051f86d7c9c388f704866b3d512cd7df97ac3516c65279523c4e`

Notice SHA-256: `977c541bd25ffe36975dde25c028c0cd15ddf3d08243983b58e8a6a3d9447523`

## base16ct 0.2.0

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/base16ct/0.2.0/download

Notice SHA-256: `0aa8963e105e8b6e02f634484145d4e5b0f42d0a6dd05c16f8148f033383adef`

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

## base64 0.22.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/base64/0.22.1/download

Notice SHA-256: `0dd882e53de11566d50f8e8e2d5a651bcf3fabee4987d70f306233cf39094ba7`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## base64ct 1.8.3

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/base64ct/1.8.3/download

Notice SHA-256: `2d1c57bff28344b9e698f51063bc8509799cc4c99a4e0cf2aa3f7e7c3e1f9a9d`

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

## bindgen 0.72.1

License: `BSD-3-Clause`.

Source: https://crates.io/api/v1/crates/bindgen/0.72.1/download

Notice SHA-256: `c23953d9deb0a3312dbeaf6c128a657f3591acee45067612fa68405eaa4525db`

## bit-vec 0.9.1

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/bit-vec/0.9.1/download

Notice SHA-256: `8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90`

Notice SHA-256: `f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7`

## bitflags 2.13.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/bitflags/2.13.1/download

Notice SHA-256: `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## block-buffer 0.10.4

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/block-buffer/0.10.4/download

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

Notice SHA-256: `d5c22aa3118d240e877ad41c5d9fa232f9c77d757d4aac0c2f943afc0a95e0ef`

## block2 0.6.2

License: `MIT`.

Source: https://crates.io/api/v1/crates/block2/0.6.2/download

Notice SHA-256: `7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54`

## bumpalo 3.20.3

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/bumpalo/3.20.3/download

Notice SHA-256: `65f94e99ddaf4f5d1782a6dae23f35d4293a9a01444a13135a6887017d353cee`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## bytes 1.12.1

License: `MIT`.

Source: https://crates.io/api/v1/crates/bytes/1.12.1/download

Notice SHA-256: `45f522cacecb1023856e46df79ca625dfc550c94910078bd8aec6e02880b3d42`

## cc 1.4.5

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/cc/1.4.5/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## ccm 0.5.0

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/ccm/0.5.0/download

Notice SHA-256: `904801faf3f1850328af8e1aa1047b9190cc22ed40df5c87f2d93d17f847ef67`

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

## cexpr 0.6.0

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/cexpr/0.6.0/download

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

Notice SHA-256: `d9771b8c6cf4426d3846de54c1febe20907f1eeadf7adfb5ade89a83bd9ea77f`

## cfg-expr 0.20.9

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/cfg-expr/0.20.9/download

Notice SHA-256: `090a294a492ab2f41388252312a65cf2f0e423330b721a68c6665ac64766753b`

Notice SHA-256: `8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90`

## cfg-if 1.0.4

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/cfg-if/1.0.4/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## cipher 0.4.4

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/cipher/0.4.4/download

Notice SHA-256: `5c7bd92d1f096f12203dc1b601e3cb17484fa1b023e30b6b8edcc80e416237ec`

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

## clang-sys 1.9.1

License: `Apache-2.0`.

Source: https://crates.io/api/v1/crates/clang-sys/1.9.1/download

Notice SHA-256: `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`

## cmake 0.1.58

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/cmake/0.1.58/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## combine 4.6.8

License: `MIT`.

Source: https://crates.io/api/v1/crates/combine/4.6.8/download

Notice SHA-256: `9bbc1b3dc4674a9ebb12c2a62f54fe3c08672539717f8d05828f684b6cc419a3`

## const-oid 0.9.6

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/const-oid/0.9.6/download

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

Notice SHA-256: `bada9e7ed8dc00d63502053c455d7c8d7575dfb7e8277a2a832531844d900682`

## cookie-factory 0.3.3

License: `MIT`.

Source: https://crates.io/api/v1/crates/cookie-factory/0.3.3/download

Notice SHA-256: `d09216dc1ea5f273997667935a8d6514d80f00b89fb6954ecc3a43e0a6e360de`

Notice SHA-256: `fac95e33eb175ff151cde39e3f7ad52292e6acf83db22bef30d3bfad417a8846`

## core-foundation 0.10.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/core-foundation/0.10.1/download

Notice SHA-256: `62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## core-foundation-sys 0.8.7

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/core-foundation-sys/0.8.7/download

Notice SHA-256: `62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## coreaudio-rs 0.14.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/coreaudio-rs/0.14.2/download

Notice SHA-256: `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## cpal 0.18.2

License: `Apache-2.0`.

Source: https://crates.io/api/v1/crates/cpal/0.18.2/download

Notice SHA-256: `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`

## cpufeatures 0.2.17

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/cpufeatures/0.2.17/download

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

Notice SHA-256: `ae9baa7beea910273c2f384c2a6b721fb7bd02bda3436074a1072e4ee689f985`

## crc 3.4.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/crc/3.4.0/download

Notice SHA-256: `3488679340a49ecc34d342c4009d2dabf76f4a21f12aec2ca99b15805d656544`

Notice SHA-256: `470355a7eed93fcc4281ec2e0f82ca3b94e7af1e4d83629f91de8cfac34d750e`

## crc-catalog 2.5.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/crc-catalog/2.5.0/download

Notice SHA-256: `5ef8fcfb6cccec8fcae043c834099a60c8b7406408db576e026d2b7e67dc5cf5`

Notice SHA-256: `d3cdb764b98283ee7c3a3cea8d374e2a2957322374378d1f3263f4d512741fc3`

## crypto-common 0.1.7

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/crypto-common/0.1.7/download

Notice SHA-256: `3521672491a3479422d5fe1aca6645dd2984090f85da6e5205abfb18fb7a6897`

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

## ctr 0.9.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/ctr/0.9.2/download

Notice SHA-256: `63af4bea227c94d021e99427f6ca3a4b8efddadcca93ab6130f708cf6138cf68`

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

## dasp_sample 0.11.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/dasp_sample/0.11.0/download

Notice SHA-256: `756c8d2ab2dc24f256e1455b5f03937f4933d83d7bc9f2d55009fc962377d512`

Notice SHA-256: `b1d6df41ed3aa96806e74c729444d7c121d90e6660a6aed01d298e03fde475a0`

## data-encoding 2.11.1

License: `MIT`.

Source: https://crates.io/api/v1/crates/data-encoding/2.11.1/download

Notice SHA-256: `b68ad1a3367b825447089e1f8d6829b97f47a89eb78d2f4ebaef4672f5606186`

## der 0.7.10

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/der/0.7.10/download

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

Notice SHA-256: `ad64fcb9589f162720f3cc5010ad76ca6ad3764e11861f9192c489df176bb71d`

## der-parser 10.0.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/der-parser/10.0.0/download

Notice SHA-256: `a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## der_derive 0.7.3

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/der_derive/0.7.3/download

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

Notice SHA-256: `bada9e7ed8dc00d63502053c455d7c8d7575dfb7e8277a2a832531844d900682`

## deranged 0.5.8

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/deranged/0.5.8/download

Notice SHA-256: `231c837c45eb53f108fb48929e488965bc4fcc14e9ea21d35f50e6b99d98685b`

Notice SHA-256: `edd65bdd88957a205c47d53fa499eed8865a70320f0f03f6391668cb304ea376`

## digest 0.10.7

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/digest/0.10.7/download

Notice SHA-256: `9e0dfd2dd4173a530e238cb6adb37aa78c34c6bc7444e0e10c1ab5d8881f63ba`

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

## dimpl 0.6.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/dimpl/0.6.2/download

Notice SHA-256: `5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b`

Notice SHA-256: `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`

## dispatch2 0.3.1

License: `Zlib OR Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/dispatch2/0.3.1/download

Notice SHA-256: `7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54`

## displaydoc 0.2.7

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/displaydoc/0.2.7/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## dunce 1.0.5

License: `CC0-1.0 OR MIT-0 OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/dunce/1.0.5/download

Notice SHA-256: `a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499`

## either 1.18.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/either/1.18.0/download

Notice SHA-256: `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## equivalent 1.0.2

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/equivalent/1.0.2/download

Notice SHA-256: `7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## errno 0.3.14

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/errno/0.3.14/download

Notice SHA-256: `8764a597675778ddfd4e25f81b08a05dbcf089ac05662df7613fe67f150e3aa2`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## fastrand 2.5.0

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/fastrand/2.5.0/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## find-msvc-tools 0.1.12

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/find-msvc-tools/0.1.12/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## flagset 0.4.7

License: `Apache-2.0`.

Source: https://crates.io/api/v1/crates/flagset/0.4.7/download

Notice SHA-256: `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`

## foreign-types 0.3.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/foreign-types/0.3.2/download

Notice SHA-256: `333ea3aaa3cadb819f4acd9f9153f9feee060a995ca8710f32bc5bd9a4b91734`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## foreign-types-shared 0.1.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/foreign-types-shared/0.1.1/download

Notice SHA-256: `333ea3aaa3cadb819f4acd9f9153f9feee060a995ca8710f32bc5bd9a4b91734`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## form_urlencoded 1.2.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/form_urlencoded/1.2.2/download

Notice SHA-256: `20c7855c364d57ea4c97889a5e8d98470a9952dade37bd9248b9a54431670e5e`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## fs_extra 1.3.0

License: `MIT`.

Source: https://crates.io/api/v1/crates/fs_extra/1.3.0/download

Notice SHA-256: `251ea8ccb1205ce5fa847d6e264d6b6753af62de2cecf2fd9abc0eb02c7c83fc`

## futures-core 0.3.34

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/futures-core/0.3.34/download

Notice SHA-256: `275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427`

Notice SHA-256: `6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd`

## futures-task 0.3.34

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/futures-task/0.3.34/download

Notice SHA-256: `275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427`

Notice SHA-256: `6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd`

## futures-util 0.3.34

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/futures-util/0.3.34/download

Notice SHA-256: `275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427`

Notice SHA-256: `6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd`

## generic-array 0.14.7

License: `MIT`.

Source: https://crates.io/api/v1/crates/generic-array/0.14.7/download

Notice SHA-256: `c09aae9d3c77b531f56351a9947bc7446511d6b025b3255312d3e3442a9a7583`

## getrandom 0.3.4

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/getrandom/0.3.4/download

Notice SHA-256: `29e9fe5074bd27e0e5d5d110394fbbcd841baee2651a3c4b4560a632702cede4`

Notice SHA-256: `aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf`

## getrandom 0.4.3

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/getrandom/0.4.3/download

Notice SHA-256: `523a42c25d245dde9c015f882cec7f4555aad883382a6cf19b4b7d9b2cd5419b`

Notice SHA-256: `aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf`

## glob 0.3.4

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/glob/0.3.4/download

Notice SHA-256: `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## hashbrown 0.17.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/hashbrown/0.17.1/download

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

Notice SHA-256: `ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2`

## heck 0.5.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/heck/0.5.0/download

Notice SHA-256: `7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## hound 3.5.1

License: `Apache-2.0`.

Source: https://crates.io/api/v1/crates/hound/3.5.1/download

Notice SHA-256: `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`

## http 1.5.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/http/1.5.0/download

Notice SHA-256: `8bb1b50b0e5c9399ae33bd35fab2769010fa6c14e8860c729a52295d84896b7a`

Notice SHA-256: `dc91f8200e4b2a1f9261035d4c18c33c246911a6c0f7b543d75347e61b249cff`

## httparse 1.10.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/httparse/1.10.1/download

Notice SHA-256: `391a5396cec6230bfabd4ef4eb2350eb895bc5efce377a2218f5702ed020d3e3`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## icu_collections 2.3.0

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/icu_collections/2.3.0/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## icu_locale_core 2.3.0

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/icu_locale_core/2.3.0/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## icu_normalizer 2.3.0

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/icu_normalizer/2.3.0/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## icu_normalizer_data 2.3.0

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/icu_normalizer_data/2.3.0/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## icu_properties 2.3.0

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/icu_properties/2.3.0/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## icu_properties_data 2.3.0

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/icu_properties_data/2.3.0/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## icu_provider 2.3.1

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/icu_provider/2.3.1/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## idna 1.1.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/idna/1.1.0/download

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

Notice SHA-256: `b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5`

## idna_adapter 1.2.2

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/idna_adapter/1.2.2/download

Notice SHA-256: `8b43ce8accd61e9d370b5ca9e9c4f953279b5c239926c62315b40e24df51b726`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## indexmap 2.14.1

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/indexmap/2.14.1/download

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

Notice SHA-256: `ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055`

## indoc 2.0.7

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/indoc/2.0.7/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## inout 0.1.4

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/inout/0.1.4/download

Notice SHA-256: `304b898acad7f02e03d6d8832d682a3b43ee729ab5d3a069af5a36979083b6b4`

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

## is 0.9.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/is/0.9.1/download

Notice SHA-256: `5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b`

## itertools 0.13.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/itertools/0.13.0/download

Notice SHA-256: `7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## itoa 1.0.18

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/itoa/1.0.18/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## jni 0.22.4

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/jni/0.22.4/download

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

Notice SHA-256: `fea1d5bf3dd71605ce5d7d2ff695c1837e914c77195e523a86b5391716477960`

## jni-macros 0.22.4

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/jni-macros/0.22.4/download

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

Notice SHA-256: `fea1d5bf3dd71605ce5d7d2ff695c1837e914c77195e523a86b5391716477960`

## jni-sys 0.3.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/jni-sys/0.3.1/download

Notice SHA-256: `1d85bd754b04ceec93e98e890edd1fa3c6a22e81bcb32135806beeccefa51cd1`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## jni-sys 0.4.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/jni-sys/0.4.1/download

Notice SHA-256: `1d85bd754b04ceec93e98e890edd1fa3c6a22e81bcb32135806beeccefa51cd1`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## jni-sys-macros 0.4.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/jni-sys-macros/0.4.1/download

Notice SHA-256: `1d85bd754b04ceec93e98e890edd1fa3c6a22e81bcb32135806beeccefa51cd1`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## jobserver 0.1.35

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/jobserver/0.1.35/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## js-sys 0.3.104

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/js-sys/0.3.104/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## lazy_static 1.5.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/lazy_static/1.5.0/download

Notice SHA-256: `0621878e61f0d0fda054bcbe02df75192c28bde1ecc8289cbd86aeba2dd72720`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## libc 0.2.189

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/libc/0.2.189/download

Notice SHA-256: `123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## libloading 0.8.9

License: `ISC`.

Source: https://crates.io/api/v1/crates/libloading/0.8.9/download

Notice SHA-256: `b29f8b01452350c20dd1af16ef83b598fea3053578ccc1c7a0ef40e57be2620f`

## libspa 0.10.1

License: `MIT`.

Source: https://crates.io/api/v1/crates/libspa/0.10.1/download

Notice SHA-256: `c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6`

## libspa-sys 0.10.1

License: `MIT`.

Source: https://crates.io/api/v1/crates/libspa-sys/0.10.1/download

Notice SHA-256: `c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6`

## linux-raw-sys 0.12.1

License: `Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/linux-raw-sys/0.12.1/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5`

Notice SHA-256: `3290ae0fbc9ddb77d2239121d710f0bb9d31b3b4744e6d97fe01e652b4c1870b`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## litemap 0.8.3

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/litemap/0.8.3/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## log 0.4.34

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/log/0.4.34/download

Notice SHA-256: `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## mach2 0.6.0

License: `BSD-2-Clause OR MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/mach2/0.6.0/download

Notice SHA-256: `044983df14c97f2f9570766aaf977b3cdfc4a06cf1f36b776331c5ff89b4fb89`

Notice SHA-256: `3f9f0f7e5a5911a8042e32c83ff5d061ce1ffd02e8a207ec2135a44ad73b4191`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## memchr 2.8.3

License: `Unlicense OR MIT`.

Source: https://crates.io/api/v1/crates/memchr/2.8.3/download

Notice SHA-256: `01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f`

Notice SHA-256: `0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f`

## memoffset 0.9.1

License: `MIT`.

Source: https://crates.io/api/v1/crates/memoffset/0.9.1/download

Notice SHA-256: `3234ac55816264ee7b6c7ee27efd61cf0a1fe775806870e3d9b4c41ea73c5cb1`

## minimal-lexical 0.2.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/minimal-lexical/0.2.1/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90`

Notice SHA-256: `dbe1fff0fb1314b6af94f161511406275cf01c5a32441fbf24528a57a051d599`

## native-tls 0.2.18

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/native-tls/0.2.18/download

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

Notice SHA-256: `f2ad7982ddbfa8c45eb965315718c55b70b9cc311b49afacb50d5fe84173ae2c`

## ndk 0.9.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/ndk/0.9.0/download

Notice SHA-256: `508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1`

Notice SHA-256: `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`

## ndk-context 0.1.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/ndk-context/0.1.1/download

Notice SHA-256: `508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1`

Notice SHA-256: `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`

## ndk-sys 0.6.0+11769913

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/ndk-sys/0.6.0+11769913/download

Notice SHA-256: `508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1`

Notice SHA-256: `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`

## nom 7.1.3

License: `MIT`.

Source: https://crates.io/api/v1/crates/nom/7.1.3/download

Notice SHA-256: `4dbda04344456f09a7a588140455413a9ac59b6b26a1ef7cdf9c800c012d87f0`

## nom 8.0.0

License: `MIT`.

Source: https://crates.io/api/v1/crates/nom/8.0.0/download

Notice SHA-256: `4dbda04344456f09a7a588140455413a9ac59b6b26a1ef7cdf9c800c012d87f0`

## num-bigint 0.4.8

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/num-bigint/0.4.8/download

Notice SHA-256: `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## num-conv 0.2.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/num-conv/0.2.2/download

Notice SHA-256: `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594`

Notice SHA-256: `e2e245f2b566d0bfafb0f6a04c16b82d710c4e6e7d799e39bb4ef6e541b85b98`

## num-derive 0.4.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/num-derive/0.4.2/download

Notice SHA-256: `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## num-integer 0.1.47

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/num-integer/0.1.47/download

Notice SHA-256: `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## num-traits 0.2.19

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/num-traits/0.2.19/download

Notice SHA-256: `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## num_enum 0.7.6

License: `BSD-3-Clause OR MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/num_enum/0.7.6/download

Notice SHA-256: `0be96d891d00e0ae0df75d7f3289b12871c000a1f5ac744f3b570768d4bb277c`

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## num_enum_derive 0.7.6

License: `BSD-3-Clause OR MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/num_enum_derive/0.7.6/download

Notice SHA-256: `0be96d891d00e0ae0df75d7f3289b12871c000a1f5ac744f3b570768d4bb277c`

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## objc2 0.6.4

License: `MIT`.

Source: https://crates.io/api/v1/crates/objc2/0.6.4/download

Notice SHA-256: `7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54`

## objc2-audio-toolbox 0.3.2

License: `Zlib OR Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/objc2-audio-toolbox/0.3.2/download

Notice SHA-256: `7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54`

## objc2-avf-audio 0.3.2

License: `Zlib OR Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/objc2-avf-audio/0.3.2/download

Notice SHA-256: `7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54`

## objc2-core-audio 0.3.2

License: `Zlib OR Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/objc2-core-audio/0.3.2/download

Notice SHA-256: `7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54`

## objc2-core-audio-types 0.3.2

License: `Zlib OR Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/objc2-core-audio-types/0.3.2/download

Notice SHA-256: `7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54`

## objc2-core-foundation 0.3.2

License: `Zlib OR Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/objc2-core-foundation/0.3.2/download

Notice SHA-256: `7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54`

## objc2-encode 4.1.0

License: `MIT`.

Source: https://crates.io/api/v1/crates/objc2-encode/4.1.0/download

Notice SHA-256: `7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54`

## objc2-foundation 0.3.2

License: `MIT`.

Source: https://crates.io/api/v1/crates/objc2-foundation/0.3.2/download

Notice SHA-256: `23d608079a47693a26dfc8a5cb01894ad0136a50714d46221d9380aa4a4b4423`

Notice SHA-256: `259b22f571b54fed25f68ec5abd8eda223e7b0547a806f13ba797a0eabecd64f`

## oid-registry 0.8.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/oid-registry/0.8.1/download

Notice SHA-256: `a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## once_cell 1.21.4

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/once_cell/1.21.4/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## openssl 0.10.81

License: `Apache-2.0`.

Source: https://crates.io/api/v1/crates/openssl/0.10.81/download

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

Notice SHA-256: `f3d4287b4a21c5176fea2f9bd4ae800696004e2fb8e05cbc818be513f188a941`

## openssl-macros 0.1.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/openssl-macros/0.1.1/download

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

Notice SHA-256: `ea5ab440900ab271811d5c2dc02a9de6e03a6956ac5727e85c11d76df5883d30`

## openssl-probe 0.2.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/openssl-probe/0.2.1/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## openssl-sys 0.9.117

License: `MIT`.

Source: https://crates.io/api/v1/crates/openssl-sys/0.9.117/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

## opus 0.4.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/opus/0.4.0/download

Notice SHA-256: `6b3b465fa69075348ee5ffc9ba6afa93402743a4a942a463404fac25257bd3ed`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## opusic-sys 0.7.5

License: `BSD-3-Clause`.

Source: https://crates.io/api/v1/crates/opusic-sys/0.7.5/download

Notice SHA-256: `01e1167d54a096d123cf6dfbbeb19587278845c6481d2d66d545669846079551`

## pem-rfc7468 0.7.0

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/pem-rfc7468/0.7.0/download

Notice SHA-256: `90c503b61dee04e1449c323ec34c229dfb68d7adcb96c7e140ee55f70fce2d8e`

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

## percent-encoding 2.3.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/percent-encoding/2.3.2/download

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

Notice SHA-256: `b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5`

## pin-project-lite 0.2.17

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/pin-project-lite/0.2.17/download

Notice SHA-256: `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594`

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

## pipewire 0.10.1

License: `MIT`.

Source: https://crates.io/api/v1/crates/pipewire/0.10.1/download

Notice SHA-256: `c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6`

## pipewire-sys 0.10.1

License: `MIT`.

Source: https://crates.io/api/v1/crates/pipewire-sys/0.10.1/download

Notice SHA-256: `c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6`

## pkcs8 0.10.2

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/pkcs8/0.10.2/download

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

Notice SHA-256: `ad64fcb9589f162720f3cc5010ad76ca6ad3764e11861f9192c489df176bb71d`

## pkg-config 0.3.34

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/pkg-config/0.3.34/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## pocketstation 1.1.12

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/pocketstation/1.1.12/download

Notice SHA-256: `37c1efe6301b127afb9d810c5fab62bdc60f72a7fb55f7a85ae00c0b8f6c1a42`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`


## pocketstation 1.1.13

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/pocketstation/1.1.13/download

Notice SHA-256: `37c1efe6301b127afb9d810c5fab62bdc60f72a7fb55f7a85ae00c0b8f6c1a42`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## pocketstation-relay 0.1.5

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/pocketstation-relay/0.1.5/download

Notice SHA-256: `37c1efe6301b127afb9d810c5fab62bdc60f72a7fb55f7a85ae00c0b8f6c1a42`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## portable-atomic 1.15.0

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/portable-atomic/1.15.0/download

Notice SHA-256: `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594`

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

## potential_utf 0.1.6

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/potential_utf/0.1.6/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## powerfmt 0.2.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/powerfmt/0.2.0/download

Notice SHA-256: `070dbc7dda03a29296f2d58bdb9b7331af90f2abc9f31df22875d1eabaf29852`

Notice SHA-256: `155420c6403d4e0fca34105e3c03fdd6939b64c393c7ec6f95f5b72c5474eab0`

## ppv-lite86 0.2.21

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/ppv-lite86/0.2.21/download

Notice SHA-256: `0218327e7a480793ffdd4eb792379a9709e5c135c7ba267f709d6f6d4d70af0a`

Notice SHA-256: `4cada0bd02ea3692eee6f16400d86c6508bbd3bafb2b65fed0419f36d4f83e8f`

## prettyplease 0.2.37

License: `MIT OR Apache-2.0`.

Source: https://crates.io/crates/prettyplease/0.2.37

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## proc-macro-crate 3.5.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/proc-macro-crate/3.5.0/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `8ada45cd9f843acf64e4722ae262c622a2b3b3007c7310ef36ac1061a30f6adb`

## proc-macro2 1.0.107

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/proc-macro2/1.0.107/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## pyo3 0.27.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/pyo3/0.27.2/download

Notice SHA-256: `32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9`

Notice SHA-256: `afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6`

## pyo3-build-config 0.27.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/pyo3-build-config/0.27.2/download

Notice SHA-256: `32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9`

Notice SHA-256: `afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6`

## pyo3-ffi 0.27.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/pyo3-ffi/0.27.2/download

Notice SHA-256: `32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9`

Notice SHA-256: `afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6`

## pyo3-macros 0.27.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/pyo3-macros/0.27.2/download

Notice SHA-256: `32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9`

Notice SHA-256: `afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6`

## pyo3-macros-backend 0.27.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/pyo3-macros-backend/0.27.2/download

Notice SHA-256: `32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9`

Notice SHA-256: `afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6`

## quote 1.0.47

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/quote/1.0.47/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## r-efi 5.3.0

License: `MIT OR Apache-2.0 OR LGPL-2.1-or-later`.

Source: https://crates.io/api/v1/crates/r-efi/5.3.0/download

Notice SHA-256: `ff92bed461f50338dd703a9ba9aee496a425957873df1d91192776e4bdf5dda7`

## r-efi 6.0.0

License: `MIT OR Apache-2.0 OR LGPL-2.1-or-later`.

Source: https://crates.io/api/v1/crates/r-efi/6.0.0/download

Notice SHA-256: `d027e91dbc9cdbb2f1190068e498bd6b61cff022b6a032b191021ba658d96111`

## rand 0.9.5

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/rand/0.9.5/download

Notice SHA-256: `209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b`

Notice SHA-256: `35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab`

Notice SHA-256: `90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5`

## rand_chacha 0.9.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/rand_chacha/0.9.0/download

Notice SHA-256: `209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b`

Notice SHA-256: `35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab`

Notice SHA-256: `90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5`

## rand_core 0.9.5

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/rand_core/0.9.5/download

Notice SHA-256: `209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b`

Notice SHA-256: `6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51`

Notice SHA-256: `90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5`

## rcgen 0.14.10

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/rcgen/0.14.10/download

Notice SHA-256: `debe6fed7ac143217c7f533759c54b14f18cd01d5fe195c51d83c2ae2d136cb4`

## regex 1.13.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/regex/1.13.1/download

Notice SHA-256: `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## regex-automata 0.4.18

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/regex-automata/0.4.18/download

Notice SHA-256: `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## regex-syntax 0.8.11

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/regex-syntax/0.8.11/download

Notice SHA-256: `6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb`

Notice SHA-256: `74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## rtrb 0.3.5

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/rtrb/0.3.5/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## rustc-hash 2.1.3

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/rustc-hash/2.1.3/download

Notice SHA-256: `30fefc3a7d6a0041541858293bcbea2dde4caa4c0a5802f996a7f7e8c0085652`

Notice SHA-256: `95bd3988beee069fa2848f648dab43cc6e0b2add2ad6bcb17360caf749802bcc`

## rustc_version 0.4.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/rustc_version/0.4.1/download

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

Notice SHA-256: `c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5`

## rusticata-macros 4.1.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/rusticata-macros/4.1.0/download

Notice SHA-256: `a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## rustix 1.1.4

License: `Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/rustix/1.1.4/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5`

Notice SHA-256: `377c2e7c53250cc5905c0b0532d35973392af16ffb9596a41d99d202cf3617c9`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## rustls-pki-types 1.15.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/rustls-pki-types/1.15.1/download

Notice SHA-256: `45fd05c4865e7c350b98ad7ac50e1b15462d49af4a91e9b0c9dd933dc9a69742`

Notice SHA-256: `9117d922e667125508dde62b02c1f57ed22f5ad21eb536aa2e2d99e1c796e639`

## rustversion 1.0.23

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/rustversion/1.0.23/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## same-file 1.0.6

License: `Unlicense OR MIT`.

Source: https://crates.io/api/v1/crates/same-file/1.0.6/download

Notice SHA-256: `01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f`

Notice SHA-256: `cb3c929a05e6cbc9de9ab06a4c57eeb60ca8c724bef6c138c87d3a577e27aa14`

## schannel 0.1.29

License: `MIT`.

Source: https://crates.io/api/v1/crates/schannel/0.1.29/download

Notice SHA-256: `aa72991ac35b4de0034da0afe943e62b48c4092fc2ba13ae47806d8e9a4ad551`

## sctp-proto 0.9.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/sctp-proto/0.9.1/download

Notice SHA-256: `7a6631daa22a9f1772e4a474ede9c3374a6c7a89b61c8b5973f7fd5ccd5cee8c`

Notice SHA-256: `814d11eba59f964bca7e74ef94f0d1eff1d5f322f895fb9b5d7e06f77debf3b2`

## sec1 0.7.3

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/sec1/0.7.3/download

Notice SHA-256: `4a883ecc3bb1010faed542bf63d53e530fea5e5e12cf676aed588784298ba929`

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

## security-framework 3.7.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/security-framework/3.7.0/download

Notice SHA-256: `91e934255ba3b2f21103d68c5581c23ef34aa95c4628e4405b8c901935e11c69`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## security-framework-sys 2.17.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/security-framework-sys/2.17.0/download

Notice SHA-256: `91e934255ba3b2f21103d68c5581c23ef34aa95c4628e4405b8c901935e11c69`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## semver 1.0.28

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/semver/1.0.28/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## serde 1.0.229

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/serde/1.0.229/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## serde_core 1.0.229

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/serde_core/1.0.229/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## serde_derive 1.0.229

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/serde_derive/1.0.229/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## serde_json 1.0.151

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/serde_json/1.0.151/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## serde_spanned 1.1.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/serde_spanned/1.1.1/download

Notice SHA-256: `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## sha1 0.10.7

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/sha1/0.10.7/download

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

Notice SHA-256: `b4eb00df6e2a4d22518fcaa6a2b4646f249b3a3c9814509b22bd2091f1392ff1`

## shlex 1.3.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/shlex/1.3.0/download

Notice SHA-256: `4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1`

Notice SHA-256: `553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583`

## shlex 2.0.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/shlex/2.0.1/download

Notice SHA-256: `4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1`

Notice SHA-256: `553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583`

## signature 2.2.0

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/signature/2.2.0/download

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

Notice SHA-256: `b3470648aff02beb36d7a53240fc9260ed80ed93bd43bace6b67d7ef7336ee33`

## simd_cesu8 1.2.0

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/simd_cesu8/1.2.0/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## simdutf8 0.1.5

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/simdutf8/0.1.5/download

Notice SHA-256: `0cec06e0e55fbc3dc5cee4fca9b607f66cb8f4e4dbcf3b3c013594dd156732e9`

Notice SHA-256: `1847e0e0698142ed4347c1441a9fa81c8fbddd44b1d8bbcd5e3647f991759d7f`

## slab 0.4.12

License: `MIT`.

Source: https://crates.io/api/v1/crates/slab/0.4.12/download

Notice SHA-256: `8ce0830173fdac609dfb4ea603fdc002c2f4af0dc9b1a005653f5da9cf534b18`

## smallvec 1.16.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/smallvec/1.16.0/download

Notice SHA-256: `0b28172679e0009b655da42797c03fd163a3379d5cfa67ba1f1655e974a2a1a9`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## spki 0.7.3

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/spki/0.7.3/download

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

Notice SHA-256: `c995204cc6bad2ed67dd41f7d89bb9f1a9d48e0edd745732b30640d7912089a4`

## stable_deref_trait 1.2.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/stable_deref_trait/1.2.1/download

Notice SHA-256: `5e05b024f653a5ce199e77cbbbd42fb5553562ec714b819421ed0c3e552a75d7`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## str0m 0.20.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/str0m/0.20.0/download

Notice SHA-256: `5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## str0m-aws-lc-rs 0.4.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/str0m-aws-lc-rs/0.4.1/download

Notice SHA-256: `5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b`

## str0m-proto 0.5.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/str0m-proto/0.5.1/download

Notice SHA-256: `5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b`

## subtle 2.6.1

License: `BSD-3-Clause`.

Source: https://crates.io/api/v1/crates/subtle/2.6.1/download

Notice SHA-256: `d1fc1bc0d155df60b2e7705b6b2ae02a05c96f948e1cec6e2fb86360b09f346b`

## syn 2.0.119

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/syn/2.0.119/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## syn 3.0.4

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/syn/3.0.4/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## synstructure 0.13.2

License: `MIT`.

Source: https://crates.io/api/v1/crates/synstructure/0.13.2/download

Notice SHA-256: `219920e865eee70b7dcfc948a86b099e7f4fe2de01bcca2ca9a20c0a033f2b59`

## system-deps 7.0.8

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/system-deps/7.0.8/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## target-lexicon 0.13.5

License: `Apache-2.0 WITH LLVM-exception`.

Source: https://crates.io/api/v1/crates/target-lexicon/0.13.5/download

Notice SHA-256: `268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5`

## tempfile 3.27.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/tempfile/3.27.0/download

Notice SHA-256: `8b427f5bc501764575e52ba4f9d95673cf8f6d80a86d0d06599852e1a9a20a36`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## thiserror 1.0.69

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/thiserror/1.0.69/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## thiserror 2.0.20

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/thiserror/2.0.20/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## thiserror-impl 1.0.69

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/thiserror-impl/1.0.69/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## thiserror-impl 2.0.20

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/thiserror-impl/2.0.20/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## time 0.3.55

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/time/0.3.55/download

Notice SHA-256: `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594`

Notice SHA-256: `2537228d9a1b44a5dc595241349cae7090b326c8de165aaf89bfddef4a00d0fc`

## time-core 0.1.9

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/time-core/0.1.9/download

Notice SHA-256: `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594`

Notice SHA-256: `2537228d9a1b44a5dc595241349cae7090b326c8de165aaf89bfddef4a00d0fc`

## time-macros 0.2.32

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/time-macros/0.2.32/download

Notice SHA-256: `0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594`

Notice SHA-256: `2537228d9a1b44a5dc595241349cae7090b326c8de165aaf89bfddef4a00d0fc`

## tinystr 0.8.4

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/tinystr/0.8.4/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## tokio 1.53.1

License: `MIT`.

Source: https://crates.io/api/v1/crates/tokio/1.53.1/download

Notice SHA-256: `253cd04c6714889df2d32f3f64d669179a1c95c76ac43c40882c52eb06bc3552`

## tokio-macros 2.7.2

License: `MIT`.

Source: https://crates.io/api/v1/crates/tokio-macros/2.7.2/download

Notice SHA-256: `0b83dc40cba89b9922bb84b0a9c7d2768ce37c1d7e138b7424fd4549915778c9`

## toml 1.1.5+spec-1.1.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/toml/1.1.5+spec-1.1.0/download

Notice SHA-256: `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## toml_datetime 1.1.1+spec-1.1.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/toml_datetime/1.1.1+spec-1.1.0/download

Notice SHA-256: `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## toml_edit 0.25.13+spec-1.1.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/toml_edit/0.25.13+spec-1.1.0/download

Notice SHA-256: `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## toml_parser 1.1.3+spec-1.1.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/toml_parser/1.1.3+spec-1.1.0/download

Notice SHA-256: `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## toml_writer 1.1.2+spec-1.1.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/toml_writer/1.1.2+spec-1.1.0/download

Notice SHA-256: `6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6`

Notice SHA-256: `c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08`

## tracing 0.1.44

License: `MIT`.

Source: https://crates.io/api/v1/crates/tracing/0.1.44/download

Notice SHA-256: `898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1`

## tracing-attributes 0.1.31

License: `MIT`.

Source: https://crates.io/api/v1/crates/tracing-attributes/0.1.31/download

Notice SHA-256: `898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1`

## tracing-core 0.1.36

License: `MIT`.

Source: https://crates.io/api/v1/crates/tracing-core/0.1.36/download

Notice SHA-256: `58545fed1565e42d687aecec6897d35c6d37ccb71479a137c0deb2203e125c79`

Notice SHA-256: `898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1`

## tungstenite 0.29.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/tungstenite/0.29.0/download

Notice SHA-256: `7fea0ee51a4ca5d5cea7464135fd55e8b09caf3a61da3d451ac8a22af95c033f`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## typenum 1.20.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/typenum/1.20.1/download

Notice SHA-256: `516b24e051bf5630880ebbd55c40a25ce9552ebaf8970a53e8976eb70e522406`

Notice SHA-256: `a825bd853ab71619a4923d7b4311221427848070ff44d990da39b0b274c1683f`

Notice SHA-256: `db11fec9946737df39ca3898d9cd8c10ec6f6c3a884a6802b0ad0b81b4e8f23a`

## unicode-ident 1.0.24

License: `(MIT OR Apache-2.0) AND Unicode-3.0`.

Source: https://crates.io/api/v1/crates/unicode-ident/1.0.24/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

Notice SHA-256: `f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1`

## unicode-width 0.2.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/unicode-width/0.2.2/download

Notice SHA-256: `23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d`

Notice SHA-256: `7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## unindent 0.2.4

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/unindent/0.2.4/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a`

## untrusted 0.7.1

License: `ISC`.

Source: https://crates.io/api/v1/crates/untrusted/0.7.1/download

Notice SHA-256: `7abd9b6960dcf7d4d0a48606a5b71bfe37d472db68d70637f3a58a56785f1621`

## url 2.5.8

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/url/2.5.8/download

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

Notice SHA-256: `b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5`

## utf8_iter 1.0.4

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/utf8_iter/1.0.4/download

Notice SHA-256: `3fa4ca83dcc9237839b1bdeb2e6d16bdfb5ec0c5ce42b24694d8bbf0dcbef72c`

Notice SHA-256: `c30152c94a6d75e021adbc52b3a52470366a46edb917e17deae3259251af244c`

Notice SHA-256: `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`

## vcpkg 0.2.15

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/vcpkg/0.2.15/download

Notice SHA-256: `016d20f335060a70e79d9fcf8dfaa6201114d65d592211f4bdfb8ae9ca2bc1dc`

Notice SHA-256: `60c93a31f490375aadf64098b75f10715010379541021e00261045d7800611d3`

## version-compare 0.2.1

License: `MIT`.

Source: https://crates.io/api/v1/crates/version-compare/0.2.1/download

Notice SHA-256: `cedfcc7ace1639adb054bd4a19b6f8585ccb2429a60b4bf51bfeb0601058c22c`

## version_check 0.9.5

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/version_check/0.9.5/download

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

Notice SHA-256: `b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e`

## walkdir 2.5.0

License: `Unlicense OR MIT`.

Source: https://crates.io/api/v1/crates/walkdir/2.5.0/download

Notice SHA-256: `01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f`

Notice SHA-256: `0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f`

## wasapi 0.23.0

License: `MIT`.

Source: https://crates.io/api/v1/crates/wasapi/0.23.0/download

Notice SHA-256: `55c8990ea1221b3f21cb1e603e97f8ea268cc8db082999ed59e39fc43d45fedf`

## wasip2 1.0.4+wasi-0.2.12

License: `Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/wasip2/1.0.4+wasi-0.2.12/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## wasm-bindgen 0.2.127

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/wasm-bindgen/0.2.127/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## wasm-bindgen-macro 0.2.127

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/wasm-bindgen-macro/0.2.127/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## wasm-bindgen-macro-support 0.2.127

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/wasm-bindgen-macro-support/0.2.127/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## wasm-bindgen-shared 0.2.127

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/wasm-bindgen-shared/0.2.127/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## web-sys 0.3.104

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/web-sys/0.3.104/download

Notice SHA-256: `378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## webrtc-audio-processing 2.1.0

License: `BSD-3-Clause`.

Source: https://crates.io/crates/webrtc-audio-processing/2.1.0

Notice SHA-256: `6db9d4840c6ff0fb3c37ace8e32cfd3eb6c6e759c67b4ecbee969cd8d75154a9`

## webrtc-audio-processing-config 2.1.0

License: `BSD-3-Clause`.

Source: https://crates.io/crates/webrtc-audio-processing-config/2.1.0

Notice SHA-256: `9b79539028e216e813e152d45f5c1ed5fdd0554426ad50270fb03134e7082dac`

## webrtc-audio-processing-sys 2.1.0

License: `BSD-3-Clause AND Apache-2.0 AND LicenseRef-WebRTC-Bundled`.

Source: https://crates.io/crates/webrtc-audio-processing-sys/2.1.0

Notice SHA-256: `01462e2068d1a04c2274f3389773014c14ed9bc3446b28303543bd3e3c064145`

Notice SHA-256: `25b7731b70c77ecd5f3bb19303fbaa99be18860f81d44f71da670fdcd04829db`

Notice SHA-256: `41d791701e3e1c1073470403de7e342442d1e6a2af72681023b13a2f45f2125c`

Notice SHA-256: `6fdbabd2c95c5efc6f1e46175278239afb9343120a3022ed0e0cb04267a6aeb3`

Notice SHA-256: `9b79539028e216e813e152d45f5c1ed5fdd0554426ad50270fb03134e7082dac`

Notice SHA-256: `a46200592eb193853527250da098e6bb0c75424e7a2c7db8da526c4f301c3d88`

Notice SHA-256: `ab00a482b6a3902e40211b43c5d0441962ea99b6cc7c25c0f243fa270b78d482`

Notice SHA-256: `c79a7fea0e3cac04cd43f20e7b648e5a0ff8fa5344e644b0ee09ca1162b62747`

Notice SHA-256: `e2f59ff41d9d03adc3dcf3deff170f8c8cf4a6eb4a9b174762a7656d23200ffa`

## winapi-util 0.1.11

License: `Unlicense OR MIT`.

Source: https://crates.io/api/v1/crates/winapi-util/0.1.11/download

Notice SHA-256: `01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f`

Notice SHA-256: `cb3c929a05e6cbc9de9ab06a4c57eeb60ca8c724bef6c138c87d3a577e27aa14`

## windows 0.58.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows/0.58.0/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows 0.62.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows/0.62.2/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-collections 0.3.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-collections/0.3.2/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-core 0.58.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-core/0.58.0/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-core 0.62.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-core/0.62.2/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-future 0.3.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-future/0.3.2/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-implement 0.58.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-implement/0.58.0/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-implement 0.60.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-implement/0.60.2/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-interface 0.58.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-interface/0.58.0/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-interface 0.59.3

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-interface/0.59.3/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-link 0.2.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-link/0.2.1/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-numerics 0.3.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-numerics/0.3.1/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-result 0.2.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-result/0.2.0/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-result 0.4.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-result/0.4.1/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-strings 0.1.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-strings/0.1.0/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-strings 0.5.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-strings/0.5.1/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-sys 0.61.2

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-sys/0.61.2/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-targets 0.52.6

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-targets/0.52.6/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows-threading 0.2.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows-threading/0.2.1/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows_aarch64_gnullvm 0.52.6

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows_aarch64_gnullvm/0.52.6/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows_aarch64_msvc 0.52.6

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows_aarch64_msvc/0.52.6/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows_i686_gnu 0.52.6

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows_i686_gnu/0.52.6/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows_i686_gnullvm 0.52.6

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows_i686_gnullvm/0.52.6/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows_i686_msvc 0.52.6

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows_i686_msvc/0.52.6/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows_x86_64_gnu 0.52.6

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows_x86_64_gnu/0.52.6/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows_x86_64_gnullvm 0.52.6

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows_x86_64_gnullvm/0.52.6/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## windows_x86_64_msvc 0.52.6

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/windows_x86_64_msvc/0.52.6/download

Notice SHA-256: `c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b`

Notice SHA-256: `c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383`

## winnow 1.0.4

License: `MIT`.

Source: https://crates.io/api/v1/crates/winnow/1.0.4/download

Notice SHA-256: `cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d`

## wit-bindgen 0.57.1

License: `Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/wit-bindgen/0.57.1/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

Notice SHA-256: `268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## writeable 0.6.4

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/writeable/0.6.4/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## x509-cert 0.2.5

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/x509-cert/0.2.5/download

Notice SHA-256: `90c503b61dee04e1449c323ec34c229dfb68d7adcb96c7e140ee55f70fce2d8e`

Notice SHA-256: `a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5`

## x509-parser 0.18.1

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/x509-parser/0.18.1/download

Notice SHA-256: `a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## yasna 0.6.0

License: `MIT OR Apache-2.0`.

Source: https://crates.io/api/v1/crates/yasna/0.6.0/download

Notice SHA-256: `2a7df90e60fd5512b8bca35d3ce90e068f21c52d962855053fd1d9e2e7ca0f16`

Notice SHA-256: `a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2`

## yoke 0.8.3

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/yoke/0.8.3/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## yoke-derive 0.8.2

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/yoke-derive/0.8.2/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## zerocopy 0.8.56

License: `BSD-2-Clause OR Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/zerocopy/0.8.56/download

Notice SHA-256: `1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df`

Notice SHA-256: `83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32`

Notice SHA-256: `9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3`

## zerocopy-derive 0.8.56

License: `BSD-2-Clause OR Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/zerocopy-derive/0.8.56/download

Notice SHA-256: `1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df`

Notice SHA-256: `83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32`

Notice SHA-256: `9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3`

## zerofrom 0.1.8

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/zerofrom/0.1.8/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## zerofrom-derive 0.1.7

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/zerofrom-derive/0.1.7/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## zeroize 1.9.0

License: `Apache-2.0 OR MIT`.

Source: https://crates.io/api/v1/crates/zeroize/1.9.0/download

Notice SHA-256: `8c7516d4b27b1e495be5e38b612298b63de48d05f49cdac94f70f3cd70f8864b`

Notice SHA-256: `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`

## zerotrie 0.2.5

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/zerotrie/0.2.5/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## zerovec 0.11.8

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/zerovec/0.11.8/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## zerovec-derive 0.11.6

License: `Unicode-3.0`.

Source: https://crates.io/api/v1/crates/zerovec-derive/0.11.6/download

Notice SHA-256: `f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2`

## zmij 1.0.23

License: `MIT`.

Source: https://crates.io/api/v1/crates/zmij/1.0.23/download

Notice SHA-256: `23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3`

## alsa-lib 1.2.15.3-1.el9

License: `LGPL-2.1-or-later`.

Source: https://repo.almalinux.org/vault/9.8/AppStream/Source/Packages/alsa-lib-1.2.15.3-1.el9.src.rpm

Notice SHA-256: `32434afcc8666ba060e111d715bfdb6c2d5dd8a35fa4d3ab8ad67d8f850d2f2b`

## openssl-libs 3.5.8-1.el9_8

License: `Apache-2.0`.

Source: https://repo.almalinux.org/vault/9.8/BaseOS/Source/Packages/openssl-3.5.8-1.el9_8.src.rpm

Notice SHA-256: `7d5450cb2d142651b8afa315b5f238efc805dad827d91ba367d8516bc9d49e7a`

## pipewire-libs 1.4.11-1.el9_8.2

License: `MIT`.

Source: https://repo.almalinux.org/vault/9.8/AppStream/Source/Packages/pipewire-1.4.11-1.el9_8.2.src.rpm

Notice SHA-256: `8909c319a7e27dbb33a15b9035f89ab3b7b2f6a12f8bcddc755206a8db1ada44`

Notice SHA-256: `be4be5d77424833edf31f53fc1f1cecb6996b9e2d747d9e6fb8f878362ebc92b`

## Notice 01462e2068d1a04c2274f3389773014c14ed9bc3446b28303543bd3e3c064145

<!-- notice:01462e2068d1a04c2274f3389773014c14ed9bc3446b28303543bd3e3c064145 -->
Additional IP Rights Grant (Patents)

"This implementation" means the copyrightable works distributed by
Google as part of the WebRTC code package.

Google hereby grants to you a perpetual, worldwide, non-exclusive,
no-charge, irrevocable (except as stated in this section) patent
license to make, have made, use, offer to sell, sell, import,
transfer, and otherwise run, modify and propagate the contents of this
implementation of the WebRTC code package, where such license applies
only to those patent claims, both currently owned by Google and
acquired in the future, licensable by Google that are necessarily
infringed by this implementation of the WebRTC code package. This
grant does not include claims that would be infringed only as a
consequence of further modification of this implementation. If you or
your agent or exclusive licensee institute or order or agree to the
institution of patent litigation against any entity (including a
cross-claim or counterclaim in a lawsuit) alleging that this
implementation of the WebRTC code package or any code incorporated
within this implementation of the WebRTC code package constitutes
direct or contributory patent infringement, or inducement of patent
infringement, then any patent rights granted to you under this License
for this implementation of the WebRTC code package shall terminate as
of the date such litigation is filed.

<!-- /notice:01462e2068d1a04c2274f3389773014c14ed9bc3446b28303543bd3e3c064145 -->

## Notice 016d20f335060a70e79d9fcf8dfaa6201114d65d592211f4bdfb8ae9ca2bc1dc

<!-- notice:016d20f335060a70e79d9fcf8dfaa6201114d65d592211f4bdfb8ae9ca2bc1dc -->
Copyright (c) 2017 Jim McGrath

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.


<!-- /notice:016d20f335060a70e79d9fcf8dfaa6201114d65d592211f4bdfb8ae9ca2bc1dc -->

## Notice 01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f

<!-- notice:01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f -->
This project is dual-licensed under the Unlicense and MIT licenses.

You may use this code under the terms of either license.

<!-- /notice:01c266bced4a434da0051174d6bee16a4c82cf634e2679b6155d40d75012390f -->

## Notice 01e1167d54a096d123cf6dfbbeb19587278845c6481d2d66d545669846079551

<!-- notice:01e1167d54a096d123cf6dfbbeb19587278845c6481d2d66d545669846079551 -->
Copyright 2001-2023 Xiph.Org, Skype Limited, Octasic,
                    Jean-Marc Valin, Timothy B. Terriberry,
                    CSIRO, Gregory Maxwell, Mark Borgerding,
                    Erik de Castro Lopo, Mozilla, Amazon

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

- Neither the name of Internet Society, IETF or IETF Trust, nor the
names of specific contributors, may be used to endorse or promote
products derived from this software without specific prior written
permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Opus is subject to the royalty-free patent licenses which are
specified at:

Xiph.Org Foundation:
https://datatracker.ietf.org/ipr/1524/

Microsoft Corporation:
https://datatracker.ietf.org/ipr/1914/

Broadcom Corporation:
https://datatracker.ietf.org/ipr/1526/

<!-- /notice:01e1167d54a096d123cf6dfbbeb19587278845c6481d2d66d545669846079551 -->

## Notice 0218327e7a480793ffdd4eb792379a9709e5c135c7ba267f709d6f6d4d70af0a

<!-- notice:0218327e7a480793ffdd4eb792379a9709e5c135c7ba267f709d6f6d4d70af0a -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright 2019 The CryptoCorrosion Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:0218327e7a480793ffdd4eb792379a9709e5c135c7ba267f709d6f6d4d70af0a -->

## Notice 044983df14c97f2f9570766aaf977b3cdfc4a06cf1f36b776331c5ff89b4fb89

<!-- notice:044983df14c97f2f9570766aaf977b3cdfc4a06cf1f36b776331c5ff89b4fb89 -->
Copyright (c) 2019 Nick Fitzgerald, 2021 Yuki Okushi
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

<!-- /notice:044983df14c97f2f9570766aaf977b3cdfc4a06cf1f36b776331c5ff89b4fb89 -->

## Notice 0621878e61f0d0fda054bcbe02df75192c28bde1ecc8289cbd86aeba2dd72720

<!-- notice:0621878e61f0d0fda054bcbe02df75192c28bde1ecc8289cbd86aeba2dd72720 -->
Copyright (c) 2010 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:0621878e61f0d0fda054bcbe02df75192c28bde1ecc8289cbd86aeba2dd72720 -->

## Notice 070dbc7dda03a29296f2d58bdb9b7331af90f2abc9f31df22875d1eabaf29852

<!-- notice:070dbc7dda03a29296f2d58bdb9b7331af90f2abc9f31df22875d1eabaf29852 -->
Copyright (c) 2023 Jacob Pratt et al.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:070dbc7dda03a29296f2d58bdb9b7331af90f2abc9f31df22875d1eabaf29852 -->

## Notice 090a294a492ab2f41388252312a65cf2f0e423330b721a68c6665ac64766753b

<!-- notice:090a294a492ab2f41388252312a65cf2f0e423330b721a68c6665ac64766753b -->
Copyright (c) 2019 Embark Studios

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:090a294a492ab2f41388252312a65cf2f0e423330b721a68c6665ac64766753b -->

## Notice 0aa8963e105e8b6e02f634484145d4e5b0f42d0a6dd05c16f8148f033383adef

<!-- notice:0aa8963e105e8b6e02f634484145d4e5b0f42d0a6dd05c16f8148f033383adef -->
Copyright (c) 2014 Steve "Sc00bz" Thomas (steve at tobtu dot com)
Copyright (c) 2022 The RustCrypto Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:0aa8963e105e8b6e02f634484145d4e5b0f42d0a6dd05c16f8148f033383adef -->

## Notice 0b28172679e0009b655da42797c03fd163a3379d5cfa67ba1f1655e974a2a1a9

<!-- notice:0b28172679e0009b655da42797c03fd163a3379d5cfa67ba1f1655e974a2a1a9 -->
Copyright (c) 2018 The Servo Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:0b28172679e0009b655da42797c03fd163a3379d5cfa67ba1f1655e974a2a1a9 -->

## Notice 0b83dc40cba89b9922bb84b0a9c7d2768ce37c1d7e138b7424fd4549915778c9

<!-- notice:0b83dc40cba89b9922bb84b0a9c7d2768ce37c1d7e138b7424fd4549915778c9 -->
MIT License

Copyright (c) 2019 Yoshua Wuyts
Copyright (c) Tokio Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:0b83dc40cba89b9922bb84b0a9c7d2768ce37c1d7e138b7424fd4549915778c9 -->

## Notice 0be96d891d00e0ae0df75d7f3289b12871c000a1f5ac744f3b570768d4bb277c

<!-- notice:0be96d891d00e0ae0df75d7f3289b12871c000a1f5ac744f3b570768d4bb277c -->
Copyright (c) 2018, Daniel Wagner-Hall
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of num_enum nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

<!-- /notice:0be96d891d00e0ae0df75d7f3289b12871c000a1f5ac744f3b570768d4bb277c -->

## Notice 0cec06e0e55fbc3dc5cee4fca9b607f66cb8f4e4dbcf3b3c013594dd156732e9

<!-- notice:0cec06e0e55fbc3dc5cee4fca9b607f66cb8f4e4dbcf3b3c013594dd156732e9 -->

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS
<!-- /notice:0cec06e0e55fbc3dc5cee4fca9b607f66cb8f4e4dbcf3b3c013594dd156732e9 -->

## Notice 0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594

<!-- notice:0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594 -->

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

<!-- /notice:0d542e0c8804e39aa7f37eb00da5a762149dc682d7829451287e11b938e94594 -->

## Notice 0dd882e53de11566d50f8e8e2d5a651bcf3fabee4987d70f306233cf39094ba7

<!-- notice:0dd882e53de11566d50f8e8e2d5a651bcf3fabee4987d70f306233cf39094ba7 -->
The MIT License (MIT)

Copyright (c) 2015 Alice Maz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

<!-- /notice:0dd882e53de11566d50f8e8e2d5a651bcf3fabee4987d70f306233cf39094ba7 -->

## Notice 0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f

<!-- notice:0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f -->
The MIT License (MIT)

Copyright (c) 2015 Andrew Gallant

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

<!-- /notice:0f96a83840e146e43c0ec96a22ec1f392e0680e6c1226e6f3ba87e0740af850f -->

## Notice 123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e

<!-- notice:123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e -->
Copyright (c) The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:123a331b5dbf04c30097fa43b8f858bc85df671fe776de498d01f3d6b7c1f69e -->

## Notice 155420c6403d4e0fca34105e3c03fdd6939b64c393c7ec6f95f5b72c5474eab0

<!-- notice:155420c6403d4e0fca34105e3c03fdd6939b64c393c7ec6f95f5b72c5474eab0 -->

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2023 Jacob Pratt et al.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

<!-- /notice:155420c6403d4e0fca34105e3c03fdd6939b64c393c7ec6f95f5b72c5474eab0 -->

## Notice 1847e0e0698142ed4347c1441a9fa81c8fbddd44b1d8bbcd5e3647f991759d7f

<!-- notice:1847e0e0698142ed4347c1441a9fa81c8fbddd44b1d8bbcd5e3647f991759d7f -->
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
<!-- /notice:1847e0e0698142ed4347c1441a9fa81c8fbddd44b1d8bbcd5e3647f991759d7f -->

## Notice 1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df

<!-- notice:1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df -->
Copyright 2023 The Fuchsia Authors

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.


<!-- /notice:1a2f5c12ddc934d58956aa5dbdd3255fe55fd957633ab7d0d39e4f0daa73f7df -->

## Notice 1d85bd754b04ceec93e98e890edd1fa3c6a22e81bcb32135806beeccefa51cd1

<!-- notice:1d85bd754b04ceec93e98e890edd1fa3c6a22e81bcb32135806beeccefa51cd1 -->
Copyright (c) 2015 The rust-jni-sys Developers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:1d85bd754b04ceec93e98e890edd1fa3c6a22e81bcb32135806beeccefa51cd1 -->

## Notice 209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b

<!-- notice:209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b -->
Copyright 2018 Developers of the Rand project
Copyright (c) 2014 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:209fbbe0ad52d9235e37badf9cadfe4dbdc87203179c0899e738b39ade42177b -->

## Notice 20c7855c364d57ea4c97889a5e8d98470a9952dade37bd9248b9a54431670e5e

<!-- notice:20c7855c364d57ea4c97889a5e8d98470a9952dade37bd9248b9a54431670e5e -->
Copyright (c) 2013-2016 The rust-url developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:20c7855c364d57ea4c97889a5e8d98470a9952dade37bd9248b9a54431670e5e -->

## Notice 219766b3420f49f6204143c5f3ef750888fb6de29ce5f63e909f146e90b375a2

<!-- notice:219766b3420f49f6204143c5f3ef750888fb6de29ce5f63e909f146e90b375a2 -->
MIT License

Copyright (c) 2018 diwic

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:219766b3420f49f6204143c5f3ef750888fb6de29ce5f63e909f146e90b375a2 -->

## Notice 219920e865eee70b7dcfc948a86b099e7f4fe2de01bcca2ca9a20c0a033f2b59

<!-- notice:219920e865eee70b7dcfc948a86b099e7f4fe2de01bcca2ca9a20c0a033f2b59 -->
Copyright 2016 Nika Layzell

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<!-- /notice:219920e865eee70b7dcfc948a86b099e7f4fe2de01bcca2ca9a20c0a033f2b59 -->

## Notice 231c837c45eb53f108fb48929e488965bc4fcc14e9ea21d35f50e6b99d98685b

<!-- notice:231c837c45eb53f108fb48929e488965bc4fcc14e9ea21d35f50e6b99d98685b -->
Copyright (c) 2024 Jacob Pratt et al.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:231c837c45eb53f108fb48929e488965bc4fcc14e9ea21d35f50e6b99d98685b -->

## Notice 23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d

<!-- notice:23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d -->
Licensed under the Apache License, Version 2.0
<LICENSE-APACHE or
http://www.apache.org/licenses/LICENSE-2.0> or the MIT
license <LICENSE-MIT or http://opensource.org/licenses/MIT>,
at your option. All files in the project carrying such
notice may not be copied, modified, or distributed except
according to those terms.

<!-- /notice:23860c2a7b5d96b21569afedf033469bab9fe14a1b24a35068b8641c578ce24d -->

## Notice 23d608079a47693a26dfc8a5cb01894ad0136a50714d46221d9380aa4a4b4423

<!-- notice:23d608079a47693a26dfc8a5cb01894ad0136a50714d46221d9380aa4a4b4423 -->
#![cfg(feature = "NSString")]
use objc2::{rc::Retained, runtime::ProtocolObject};
use objc2_foundation::{NSCopying, NSMutableCopying, NSString};

#[test]
fn copy() {
    let obj = NSString::new();
    let protocol_object: &ProtocolObject<dyn NSCopying> = ProtocolObject::from_ref(&*obj);
    let _: Retained<ProtocolObject<dyn NSCopying>> = protocol_object.copy();
}

#[test]
fn copy_mutable() {
    let obj = NSString::new();
    let protocol_object: &ProtocolObject<dyn NSMutableCopying> = ProtocolObject::from_ref(&*obj);
    let _: Retained<ProtocolObject<dyn NSMutableCopying>> = protocol_object.mutableCopy();
}

<!-- /notice:23d608079a47693a26dfc8a5cb01894ad0136a50714d46221d9380aa4a4b4423 -->

## Notice 23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3

<!-- notice:23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3 -->
Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:23f18e03dc49df91622fe2a76176497404e46ced8a715d9d2b67a7446571cca3 -->

## Notice 251ea8ccb1205ce5fa847d6e264d6b6753af62de2cecf2fd9abc0eb02c7c83fc

<!-- notice:251ea8ccb1205ce5fa847d6e264d6b6753af62de2cecf2fd9abc0eb02c7c83fc -->
MIT License

Copyright (c) 2017 Denis Kurilenko

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:251ea8ccb1205ce5fa847d6e264d6b6753af62de2cecf2fd9abc0eb02c7c83fc -->

## Notice 2537228d9a1b44a5dc595241349cae7090b326c8de165aaf89bfddef4a00d0fc

<!-- notice:2537228d9a1b44a5dc595241349cae7090b326c8de165aaf89bfddef4a00d0fc -->
Copyright (c) Jacob Pratt et al.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:2537228d9a1b44a5dc595241349cae7090b326c8de165aaf89bfddef4a00d0fc -->

## Notice 253cd04c6714889df2d32f3f64d669179a1c95c76ac43c40882c52eb06bc3552

<!-- notice:253cd04c6714889df2d32f3f64d669179a1c95c76ac43c40882c52eb06bc3552 -->
MIT License

Copyright (c) Tokio Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:253cd04c6714889df2d32f3f64d669179a1c95c76ac43c40882c52eb06bc3552 -->

## Notice 259b22f571b54fed25f68ec5abd8eda223e7b0547a806f13ba797a0eabecd64f

<!-- notice:259b22f571b54fed25f68ec5abd8eda223e7b0547a806f13ba797a0eabecd64f -->
use objc2::extern_protocol;
use objc2::rc::Retained;
use objc2::runtime::NSZone;
use objc2::runtime::ProtocolObject;
use objc2::Message;

/// A helper type for implementing [`NSCopying`].
///
/// `NSCopying` and `NSMutableCopying` do not in their signatures describe the
/// result type from the copying operation. This is problematic, as it means
/// that using them ends up falling back to [`AnyObject`], which makes copying
/// much less useful and ergonomic.
///
/// To properly describe this, we need an associated type which describes the
/// actual result type from a copy. The associated type can't be present
/// directly on the protocol traits themselves, however, since we want to use
/// them as e.g. `ProtocolObject<dyn NSCopying>`, so we introduce this helper
/// trait instead. See [`MutableCopyingHelper`] for the mutable variant.
///
/// We might be able to get rid of this hack once [associated type defaults]
/// are stabilized.
///
/// [`AnyObject`]: objc2::runtime::AnyObject
/// [associated type defaults]: https://github.com/rust-lang/rust/issues/29661
///
///
/// # Safety
///
/// The [`Result`] type must be correct.
///
/// [`Result`]: Self::Result
pub unsafe trait CopyingHelper: Message {
    /// The immutable counterpart of the type, or `Self` if the type has no
    /// immutable counterpart.
    ///
    /// The implementation for `NSString` has itself (`NSString`) here, while
    /// `NSMutableString` instead has `NSString`.
    type Result: Message;
}

/// A helper type for implementing [`NSMutableCopying`].
///
/// See [`CopyingHelper`] for the immutable variant, and more details in
/// general. These traits are split to allow implementing
/// `MutableCopyingHelper` only when the mutable class is available.
///
///
/// # Safety
///
/// The [`Result`] type must be correct.
///
/// [`Result`]: Self::Result
pub unsafe trait MutableCopyingHelper: Message {
    /// The mutable counterpart of the type, or `Self` if the type has no
    /// mutable counterpart.
    ///
    /// The implementation for `NSString` has `NSMutableString` here, while
    /// `NSMutableString` has itself (`NSMutableString`).
    type Result: Message;
}

// SAFETY: Superclasses are not in general required to implement the same
// traits as their subclasses, but we're not dealing with normal classes and
// arbitrary protocols, we're dealing with with immutable/mutable class
// counterparts, and the `NSCopying`/`NSMutableCopying` protocols, which
// _will_ be implemented on superclasses.
unsafe impl<P: ?Sized> CopyingHelper for ProtocolObject<P> {
    type Result = Self;
}

// SAFETY: Subclasses are required to always implement the same traits as
// their superclasses, so a mutable subclass is required to implement the same
// traits too.
unsafe impl<P: ?Sized> MutableCopyingHelper for ProtocolObject<P> {
    type Result = Self;
}

extern_protocol!(
    /// A protocol to provide functional copies of objects.
    ///
    /// This is similar to Rust's [`Clone`] trait, along with sharing a few
    /// similarities to the [`std::borrow::ToOwned`] trait with regards to the
    /// output type.
    ///
    /// To allow using this in a meaningful way in Rust, we have to "enrich"
    /// the implementation by also specifying the resulting type, see
    /// [`CopyingHelper`] for details.
    ///
    /// See also [Apple's documentation][apple-doc].
    ///
    /// [apple-doc]: https://developer.apple.com/documentation/foundation/nscopying
    ///
    ///
    /// # Examples
    ///
    /// Implement `NSCopying` for an externally defined class.
    ///
    /// ```
    /// use objc2::extern_class;
    /// use objc2_foundation::{CopyingHelper, NSCopying, NSObject};
    ///
    /// extern_class!(
    ///     #[unsafe(super(NSObject))]
    ///     # #[name = "NSData"]
    ///     struct ExampleClass;
    /// );
    ///
    /// unsafe impl NSCopying for ExampleClass {}
    ///
    /// // Copying ExampleClass returns another ExampleClass.
    /// unsafe impl CopyingHelper for ExampleClass {
    ///     type Result = Self;
    /// }
    /// ```
    ///
    /// Implement `NSCopying` for a custom class.
    ///
    /// ```
    /// use objc2::{define_class, msg_send, AnyThread, DefinedClass};
    /// use objc2::rc::Retained;
    /// use objc2::runtime::NSZone;
    /// use objc2_foundation::{CopyingHelper, NSCopying, NSObject};
    ///
    /// define_class!(
    ///     #[unsafe(super(NSObject))]
    ///     struct CustomClass;
    ///
    ///     unsafe impl NSCopying for CustomClass {
    ///         #[unsafe(method_id(copyWithZone:))]
    ///         fn copyWithZone(&self, _zone: *const NSZone) -> Retained<Self> {
    ///             // Create new class, and transfer ivars
    ///             let new = Self::alloc().set_ivars(self.ivars().clone());
    ///             unsafe { msg_send![super(new), init] }
    ///         }
    ///     }
    /// );
    ///
    /// // Copying CustomClass returns another CustomClass.
    /// unsafe impl CopyingHelper for CustomClass {
    ///     type Result = Self;
    /// }
    /// ```
    #[allow(clippy::missing_safety_doc)]
    pub unsafe trait NSCopying {
        /// Returns a new instance that's a copy of the receiver.
        ///
        /// The output type is the immutable counterpart of the object, which
        /// is usually `Self`, but e.g. `NSMutableString` returns `NSString`.
        #[unsafe(method(copy))]
        #[unsafe(method_family = copy)]
        #[optional]
        fn copy(&self) -> Retained<Self::Result>
        where
            Self: CopyingHelper;

        /// Returns a new instance that's a copy of the receiver.
        ///
        /// This is only used when implementing `NSCopying`, call
        /// [`copy`][NSCopying::copy] instead.
        ///
        ///
        /// # Safety
        ///
        /// The zone pointer must be valid or NULL.
        #[unsafe(method(copyWithZone:))]
        #[unsafe(method_family = copy)]
        unsafe fn copyWithZone(&self, zone: *mut NSZone) -> Retained<Self::Result>
        where
            Self: CopyingHelper;
    }
);

extern_protocol!(
    /// A protocol to provide mutable copies of objects.
    ///
    /// Only classes that have an “immutable vs. mutable” distinction should
    /// adopt this protocol. Use the [`MutableCopyingHelper`] trait to specify
    /// the return type after copying.
    ///
    /// See [Apple's documentation][apple-doc] for details.
    ///
    /// [apple-doc]: https://developer.apple.com/documentation/foundation/nsmutablecopying
    ///
    ///
    /// # Example
    ///
    /// Implement [`NSCopying`] and [`NSMutableCopying`] for a class pair like
    /// `NSString` and `NSMutableString`.
    ///
    /// ```ignore
    /// // Immutable copies return NSString
    ///
    /// unsafe impl NSCopying for NSString {}
    /// unsafe impl CopyingHelper for NSString {
    ///     type Result = NSString;
    /// }
    /// unsafe impl NSCopying for NSMutableString {}
    /// unsafe impl CopyingHelper for NSMutableString {
    ///     type Result = NSString;
    /// }
    ///
    /// // Mutable copies return NSMutableString
    ///
    /// unsafe impl NSMutableCopying for NSString {}
    /// unsafe impl MutableCopyingHelper for NSString {
    ///     type Result = NSMutableString;
    /// }
    /// unsafe impl NSMutableCopying for NSMutableString {}
    /// unsafe impl MutableCopyingHelper for NSMutableString {
    ///     type Result = NSMutableString;
    /// }
    /// ```
    #[allow(clippy::missing_safety_doc)]
    pub unsafe trait NSMutableCopying {
        /// Returns a new instance that's a mutable copy of the receiver.
        ///
        /// The output type is the mutable counterpart of the object. E.g. both
        /// `NSString` and `NSMutableString` return `NSMutableString`.
        #[unsafe(method(mutableCopy))]
        #[unsafe(method_family = mutableCopy)]
        #[optional]
        fn mutableCopy(&self) -> Retained<Self::Result>
        where
            Self: MutableCopyingHelper;

        /// Returns a new instance that's a mutable copy of the receiver.
        ///
        /// This is only used when implementing `NSMutableCopying`, call
        /// [`mutableCopy`][NSMutableCopying::mutableCopy] instead.
        ///
        ///
        /// # Safety
        ///
        /// The zone pointer must be valid or NULL.
        #[unsafe(method(mutableCopyWithZone:))]
        #[unsafe(method_family = mutableCopy)]
        unsafe fn mutableCopyWithZone(&self, zone: *mut NSZone) -> Retained<Self::Result>
        where
            Self: MutableCopyingHelper;
    }
);

<!-- /notice:259b22f571b54fed25f68ec5abd8eda223e7b0547a806f13ba797a0eabecd64f -->

## Notice 25b7731b70c77ecd5f3bb19303fbaa99be18860f81d44f71da670fdcd04829db

<!-- notice:25b7731b70c77ecd5f3bb19303fbaa99be18860f81d44f71da670fdcd04829db -->
/*
 * http://www.kurims.kyoto-u.ac.jp/~ooura/fft.html
 * Copyright Takuya OOURA, 1996-2001
 *
 * You may use, copy, modify and distribute this code for any purpose (include
 * commercial use) and without fee. Please refer to this package when you modify
 * this code.
 */

<!-- /notice:25b7731b70c77ecd5f3bb19303fbaa99be18860f81d44f71da670fdcd04829db -->

## Notice 268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5

<!-- notice:268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5 -->

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


--- LLVM Exceptions to the Apache 2.0 License ----

As an exception, if, as a result of your compiling your source code, portions
of this Software are embedded into an Object form of such source code, you
may redistribute such embedded portions in such Object form without complying
with the conditions of Sections 4(a), 4(b) and 4(d) of the License.

In addition, if you combine or link compiled forms of this Software with
software that is licensed under the GPLv2 ("Combined Software") and if a
court of competent jurisdiction determines that the patent provision (Section
3), the indemnity provision (Section 9) or other Section of the License
conflicts with the conditions of the GPLv2, you may retroactively and
prospectively choose to deem waived or otherwise exclude such Section(s) of
the License, but only in their entirety and only with respect to the Combined
Software.


<!-- /notice:268872b9816f90fd8e85db5a28d33f8150ebb8dd016653fb39ef1f94f2686bc5 -->

## Notice 275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427

<!-- notice:275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427 -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright (c) 2016 Alex Crichton
Copyright (c) 2017 The Tokio Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:275c491d6d1160553c32fd6127061d7f9606c3ea25abfad6ca3f6ed088785427 -->

## Notice 27995d58ad5c1145c1a8cd86244ce844886958a35eb2b78c6b772748669999ac

<!-- notice:27995d58ad5c1145c1a8cd86244ce844886958a35eb2b78c6b772748669999ac -->
Copyright (c) 2018 Josh Stone

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:27995d58ad5c1145c1a8cd86244ce844886958a35eb2b78c6b772748669999ac -->

## Notice 29e9fe5074bd27e0e5d5d110394fbbcd841baee2651a3c4b4560a632702cede4

<!-- notice:29e9fe5074bd27e0e5d5d110394fbbcd841baee2651a3c4b4560a632702cede4 -->
Copyright (c) 2018-2025 The rust-random Project Developers
Copyright (c) 2014 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:29e9fe5074bd27e0e5d5d110394fbbcd841baee2651a3c4b4560a632702cede4 -->

## Notice 2a7df90e60fd5512b8bca35d3ce90e068f21c52d962855053fd1d9e2e7ca0f16

<!-- notice:2a7df90e60fd5512b8bca35d3ce90e068f21c52d962855053fd1d9e2e7ca0f16 -->
Copyright (c) 2016 Masaki Hara

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<!-- /notice:2a7df90e60fd5512b8bca35d3ce90e068f21c52d962855053fd1d9e2e7ca0f16 -->

## Notice 2d1c57bff28344b9e698f51063bc8509799cc4c99a4e0cf2aa3f7e7c3e1f9a9d

<!-- notice:2d1c57bff28344b9e698f51063bc8509799cc4c99a4e0cf2aa3f7e7c3e1f9a9d -->
Copyright (c) 2014 Steve "Sc00bz" Thomas (steve at tobtu dot com)
Copyright (c) 2021-2025 The RustCrypto Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:2d1c57bff28344b9e698f51063bc8509799cc4c99a4e0cf2aa3f7e7c3e1f9a9d -->

## Notice 304b898acad7f02e03d6d8832d682a3b43ee729ab5d3a069af5a36979083b6b4

<!-- notice:304b898acad7f02e03d6d8832d682a3b43ee729ab5d3a069af5a36979083b6b4 -->
Copyright (c) 2022 The RustCrypto Project Developers
Copyright (c) 2022 Artyom Pavlov

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:304b898acad7f02e03d6d8832d682a3b43ee729ab5d3a069af5a36979083b6b4 -->

## Notice 30fefc3a7d6a0041541858293bcbea2dde4caa4c0a5802f996a7f7e8c0085652

<!-- notice:30fefc3a7d6a0041541858293bcbea2dde4caa4c0a5802f996a7f7e8c0085652 -->
Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
<!-- /notice:30fefc3a7d6a0041541858293bcbea2dde4caa4c0a5802f996a7f7e8c0085652 -->

## Notice 3234ac55816264ee7b6c7ee27efd61cf0a1fe775806870e3d9b4c41ea73c5cb1

<!-- notice:3234ac55816264ee7b6c7ee27efd61cf0a1fe775806870e3d9b4c41ea73c5cb1 -->
Copyright (c) 2017 Gilad Naaman

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
<!-- /notice:3234ac55816264ee7b6c7ee27efd61cf0a1fe775806870e3d9b4c41ea73c5cb1 -->

## Notice 32434afcc8666ba060e111d715bfdb6c2d5dd8a35fa4d3ab8ad67d8f850d2f2b

<!-- notice:32434afcc8666ba060e111d715bfdb6c2d5dd8a35fa4d3ab8ad67d8f850d2f2b -->
		  GNU LESSER GENERAL PUBLIC LICENSE
		       Version 2.1, February 1999

 Copyright (C) 1991, 1999 Free Software Foundation, Inc.
     51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

[This is the first released version of the Lesser GPL.  It also counts
 as the successor of the GNU Library Public License, version 2, hence
 the version number 2.1.]

			    Preamble

  The licenses for most software are designed to take away your
freedom to share and change it.  By contrast, the GNU General Public
Licenses are intended to guarantee your freedom to share and change
free software--to make sure the software is free for all its users.

  This license, the Lesser General Public License, applies to some
specially designated software packages--typically libraries--of the
Free Software Foundation and other authors who decide to use it.  You
can use it too, but we suggest you first think carefully about whether
this license or the ordinary General Public License is the better
strategy to use in any particular case, based on the explanations below.

  When we speak of free software, we are referring to freedom of use,
not price.  Our General Public Licenses are designed to make sure that
you have the freedom to distribute copies of free software (and charge
for this service if you wish); that you receive source code or can get
it if you want it; that you can change the software and use pieces of
it in new free programs; and that you are informed that you can do
these things.

  To protect your rights, we need to make restrictions that forbid
distributors to deny you these rights or to ask you to surrender these
rights.  These restrictions translate to certain responsibilities for
you if you distribute copies of the library or if you modify it.

  For example, if you distribute copies of the library, whether gratis
or for a fee, you must give the recipients all the rights that we gave
you.  You must make sure that they, too, receive or can get the source
code.  If you link other code with the library, you must provide
complete object files to the recipients, so that they can relink them
with the library after making changes to the library and recompiling
it.  And you must show them these terms so they know their rights.

  We protect your rights with a two-step method: (1) we copyright the
library, and (2) we offer you this license, which gives you legal
permission to copy, distribute and/or modify the library.

  To protect each distributor, we want to make it very clear that
there is no warranty for the free library.  Also, if the library is
modified by someone else and passed on, the recipients should know
that what they have is not the original version, so that the original
author's reputation will not be affected by problems that might be
introduced by others.

  Finally, software patents pose a constant threat to the existence of
any free program.  We wish to make sure that a company cannot
effectively restrict the users of a free program by obtaining a
restrictive license from a patent holder.  Therefore, we insist that
any patent license obtained for a version of the library must be
consistent with the full freedom of use specified in this license.

  Most GNU software, including some libraries, is covered by the
ordinary GNU General Public License.  This license, the GNU Lesser
General Public License, applies to certain designated libraries, and
is quite different from the ordinary General Public License.  We use
this license for certain libraries in order to permit linking those
libraries into non-free programs.

  When a program is linked with a library, whether statically or using
a shared library, the combination of the two is legally speaking a
combined work, a derivative of the original library.  The ordinary
General Public License therefore permits such linking only if the
entire combination fits its criteria of freedom.  The Lesser General
Public License permits more lax criteria for linking other code with
the library.

  We call this license the "Lesser" General Public License because it
does Less to protect the user's freedom than the ordinary General
Public License.  It also provides other free software developers Less
of an advantage over competing non-free programs.  These disadvantages
are the reason we use the ordinary General Public License for many
libraries.  However, the Lesser license provides advantages in certain
special circumstances.

  For example, on rare occasions, there may be a special need to
encourage the widest possible use of a certain library, so that it becomes
a de-facto standard.  To achieve this, non-free programs must be
allowed to use the library.  A more frequent case is that a free
library does the same job as widely used non-free libraries.  In this
case, there is little to gain by limiting the free library to free
software only, so we use the Lesser General Public License.

  In other cases, permission to use a particular library in non-free
programs enables a greater number of people to use a large body of
free software.  For example, permission to use the GNU C Library in
non-free programs enables many more people to use the whole GNU
operating system, as well as its variant, the GNU/Linux operating
system.

  Although the Lesser General Public License is Less protective of the
users' freedom, it does ensure that the user of a program that is
linked with the Library has the freedom and the wherewithal to run
that program using a modified version of the Library.

  The precise terms and conditions for copying, distribution and
modification follow.  Pay close attention to the difference between a
"work based on the library" and a "work that uses the library".  The
former contains code derived from the library, whereas the latter must
be combined with the library in order to run.

		  GNU LESSER GENERAL PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. This License Agreement applies to any software library or other
program which contains a notice placed by the copyright holder or
other authorized party saying it may be distributed under the terms of
this Lesser General Public License (also called "this License").
Each licensee is addressed as "you".

  A "library" means a collection of software functions and/or data
prepared so as to be conveniently linked with application programs
(which use some of those functions and data) to form executables.

  The "Library", below, refers to any such software library or work
which has been distributed under these terms.  A "work based on the
Library" means either the Library or any derivative work under
copyright law: that is to say, a work containing the Library or a
portion of it, either verbatim or with modifications and/or translated
straightforwardly into another language.  (Hereinafter, translation is
included without limitation in the term "modification".)

  "Source code" for a work means the preferred form of the work for
making modifications to it.  For a library, complete source code means
all the source code for all modules it contains, plus any associated
interface definition files, plus the scripts used to control compilation
and installation of the library.

  Activities other than copying, distribution and modification are not
covered by this License; they are outside its scope.  The act of
running a program using the Library is not restricted, and output from
such a program is covered only if its contents constitute a work based
on the Library (independent of the use of the Library in a tool for
writing it).  Whether that is true depends on what the Library does
and what the program that uses the Library does.
  
  1. You may copy and distribute verbatim copies of the Library's
complete source code as you receive it, in any medium, provided that
you conspicuously and appropriately publish on each copy an
appropriate copyright notice and disclaimer of warranty; keep intact
all the notices that refer to this License and to the absence of any
warranty; and distribute a copy of this License along with the
Library.

  You may charge a fee for the physical act of transferring a copy,
and you may at your option offer warranty protection in exchange for a
fee.

  2. You may modify your copy or copies of the Library or any portion
of it, thus forming a work based on the Library, and copy and
distribute such modifications or work under the terms of Section 1
above, provided that you also meet all of these conditions:

    a) The modified work must itself be a software library.

    b) You must cause the files modified to carry prominent notices
    stating that you changed the files and the date of any change.

    c) You must cause the whole of the work to be licensed at no
    charge to all third parties under the terms of this License.

    d) If a facility in the modified Library refers to a function or a
    table of data to be supplied by an application program that uses
    the facility, other than as an argument passed when the facility
    is invoked, then you must make a good faith effort to ensure that,
    in the event an application does not supply such function or
    table, the facility still operates, and performs whatever part of
    its purpose remains meaningful.

    (For example, a function in a library to compute square roots has
    a purpose that is entirely well-defined independent of the
    application.  Therefore, Subsection 2d requires that any
    application-supplied function or table used by this function must
    be optional: if the application does not supply it, the square
    root function must still compute square roots.)

These requirements apply to the modified work as a whole.  If
identifiable sections of that work are not derived from the Library,
and can be reasonably considered independent and separate works in
themselves, then this License, and its terms, do not apply to those
sections when you distribute them as separate works.  But when you
distribute the same sections as part of a whole which is a work based
on the Library, the distribution of the whole must be on the terms of
this License, whose permissions for other licensees extend to the
entire whole, and thus to each and every part regardless of who wrote
it.

Thus, it is not the intent of this section to claim rights or contest
your rights to work written entirely by you; rather, the intent is to
exercise the right to control the distribution of derivative or
collective works based on the Library.

In addition, mere aggregation of another work not based on the Library
with the Library (or with a work based on the Library) on a volume of
a storage or distribution medium does not bring the other work under
the scope of this License.

  3. You may opt to apply the terms of the ordinary GNU General Public
License instead of this License to a given copy of the Library.  To do
this, you must alter all the notices that refer to this License, so
that they refer to the ordinary GNU General Public License, version 2,
instead of to this License.  (If a newer version than version 2 of the
ordinary GNU General Public License has appeared, then you can specify
that version instead if you wish.)  Do not make any other change in
these notices.

  Once this change is made in a given copy, it is irreversible for
that copy, so the ordinary GNU General Public License applies to all
subsequent copies and derivative works made from that copy.

  This option is useful when you wish to copy part of the code of
the Library into a program that is not a library.

  4. You may copy and distribute the Library (or a portion or
derivative of it, under Section 2) in object code or executable form
under the terms of Sections 1 and 2 above provided that you accompany
it with the complete corresponding machine-readable source code, which
must be distributed under the terms of Sections 1 and 2 above on a
medium customarily used for software interchange.

  If distribution of object code is made by offering access to copy
from a designated place, then offering equivalent access to copy the
source code from the same place satisfies the requirement to
distribute the source code, even though third parties are not
compelled to copy the source along with the object code.

  5. A program that contains no derivative of any portion of the
Library, but is designed to work with the Library by being compiled or
linked with it, is called a "work that uses the Library".  Such a
work, in isolation, is not a derivative work of the Library, and
therefore falls outside the scope of this License.

  However, linking a "work that uses the Library" with the Library
creates an executable that is a derivative of the Library (because it
contains portions of the Library), rather than a "work that uses the
library".  The executable is therefore covered by this License.
Section 6 states terms for distribution of such executables.

  When a "work that uses the Library" uses material from a header file
that is part of the Library, the object code for the work may be a
derivative work of the Library even though the source code is not.
Whether this is true is especially significant if the work can be
linked without the Library, or if the work is itself a library.  The
threshold for this to be true is not precisely defined by law.

  If such an object file uses only numerical parameters, data
structure layouts and accessors, and small macros and small inline
functions (ten lines or less in length), then the use of the object
file is unrestricted, regardless of whether it is legally a derivative
work.  (Executables containing this object code plus portions of the
Library will still fall under Section 6.)

  Otherwise, if the work is a derivative of the Library, you may
distribute the object code for the work under the terms of Section 6.
Any executables containing that work also fall under Section 6,
whether or not they are linked directly with the Library itself.

  6. As an exception to the Sections above, you may also combine or
link a "work that uses the Library" with the Library to produce a
work containing portions of the Library, and distribute that work
under terms of your choice, provided that the terms permit
modification of the work for the customer's own use and reverse
engineering for debugging such modifications.

  You must give prominent notice with each copy of the work that the
Library is used in it and that the Library and its use are covered by
this License.  You must supply a copy of this License.  If the work
during execution displays copyright notices, you must include the
copyright notice for the Library among them, as well as a reference
directing the user to the copy of this License.  Also, you must do one
of these things:

    a) Accompany the work with the complete corresponding
    machine-readable source code for the Library including whatever
    changes were used in the work (which must be distributed under
    Sections 1 and 2 above); and, if the work is an executable linked
    with the Library, with the complete machine-readable "work that
    uses the Library", as object code and/or source code, so that the
    user can modify the Library and then relink to produce a modified
    executable containing the modified Library.  (It is understood
    that the user who changes the contents of definitions files in the
    Library will not necessarily be able to recompile the application
    to use the modified definitions.)

    b) Use a suitable shared library mechanism for linking with the
    Library.  A suitable mechanism is one that (1) uses at run time a
    copy of the library already present on the user's computer system,
    rather than copying library functions into the executable, and (2)
    will operate properly with a modified version of the library, if
    the user installs one, as long as the modified version is
    interface-compatible with the version that the work was made with.

    c) Accompany the work with a written offer, valid for at
    least three years, to give the same user the materials
    specified in Subsection 6a, above, for a charge no more
    than the cost of performing this distribution.

    d) If distribution of the work is made by offering access to copy
    from a designated place, offer equivalent access to copy the above
    specified materials from the same place.

    e) Verify that the user has already received a copy of these
    materials or that you have already sent this user a copy.

  For an executable, the required form of the "work that uses the
Library" must include any data and utility programs needed for
reproducing the executable from it.  However, as a special exception,
the materials to be distributed need not include anything that is
normally distributed (in either source or binary form) with the major
components (compiler, kernel, and so on) of the operating system on
which the executable runs, unless that component itself accompanies
the executable.

  It may happen that this requirement contradicts the license
restrictions of other proprietary libraries that do not normally
accompany the operating system.  Such a contradiction means you cannot
use both them and the Library together in an executable that you
distribute.

  7. You may place library facilities that are a work based on the
Library side-by-side in a single library together with other library
facilities not covered by this License, and distribute such a combined
library, provided that the separate distribution of the work based on
the Library and of the other library facilities is otherwise
permitted, and provided that you do these two things:

    a) Accompany the combined library with a copy of the same work
    based on the Library, uncombined with any other library
    facilities.  This must be distributed under the terms of the
    Sections above.

    b) Give prominent notice with the combined library of the fact
    that part of it is a work based on the Library, and explaining
    where to find the accompanying uncombined form of the same work.

  8. You may not copy, modify, sublicense, link with, or distribute
the Library except as expressly provided under this License.  Any
attempt otherwise to copy, modify, sublicense, link with, or
distribute the Library is void, and will automatically terminate your
rights under this License.  However, parties who have received copies,
or rights, from you under this License will not have their licenses
terminated so long as such parties remain in full compliance.

  9. You are not required to accept this License, since you have not
signed it.  However, nothing else grants you permission to modify or
distribute the Library or its derivative works.  These actions are
prohibited by law if you do not accept this License.  Therefore, by
modifying or distributing the Library (or any work based on the
Library), you indicate your acceptance of this License to do so, and
all its terms and conditions for copying, distributing or modifying
the Library or works based on it.

  10. Each time you redistribute the Library (or any work based on the
Library), the recipient automatically receives a license from the
original licensor to copy, distribute, link with or modify the Library
subject to these terms and conditions.  You may not impose any further
restrictions on the recipients' exercise of the rights granted herein.
You are not responsible for enforcing compliance by third parties with
this License.

  11. If, as a consequence of a court judgment or allegation of patent
infringement or for any other reason (not limited to patent issues),
conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot
distribute so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you
may not distribute the Library at all.  For example, if a patent
license would not permit royalty-free redistribution of the Library by
all those who receive copies directly or indirectly through you, then
the only way you could satisfy both it and this License would be to
refrain entirely from distribution of the Library.

If any portion of this section is held invalid or unenforceable under any
particular circumstance, the balance of the section is intended to apply,
and the section as a whole is intended to apply in other circumstances.

It is not the purpose of this section to induce you to infringe any
patents or other property right claims or to contest validity of any
such claims; this section has the sole purpose of protecting the
integrity of the free software distribution system which is
implemented by public license practices.  Many people have made
generous contributions to the wide range of software distributed
through that system in reliance on consistent application of that
system; it is up to the author/donor to decide if he or she is willing
to distribute software through any other system and a licensee cannot
impose that choice.

This section is intended to make thoroughly clear what is believed to
be a consequence of the rest of this License.

  12. If the distribution and/or use of the Library is restricted in
certain countries either by patents or by copyrighted interfaces, the
original copyright holder who places the Library under this License may add
an explicit geographical distribution limitation excluding those countries,
so that distribution is permitted only in or among countries not thus
excluded.  In such case, this License incorporates the limitation as if
written in the body of this License.

  13. The Free Software Foundation may publish revised and/or new
versions of the Lesser General Public License from time to time.
Such new versions will be similar in spirit to the present version,
but may differ in detail to address new problems or concerns.

Each version is given a distinguishing version number.  If the Library
specifies a version number of this License which applies to it and
"any later version", you have the option of following the terms and
conditions either of that version or of any later version published by
the Free Software Foundation.  If the Library does not specify a
license version number, you may choose any version ever published by
the Free Software Foundation.

  14. If you wish to incorporate parts of the Library into other free
programs whose distribution conditions are incompatible with these,
write to the author to ask for permission.  For software which is
copyrighted by the Free Software Foundation, write to the Free
Software Foundation; we sometimes make exceptions for this.  Our
decision will be guided by the two goals of preserving the free status
of all derivatives of our free software and of promoting the sharing
and reuse of software generally.

			    NO WARRANTY

  15. BECAUSE THE LIBRARY IS LICENSED FREE OF CHARGE, THERE IS NO
WARRANTY FOR THE LIBRARY, TO THE EXTENT PERMITTED BY APPLICABLE LAW.
EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR
OTHER PARTIES PROVIDE THE LIBRARY "AS IS" WITHOUT WARRANTY OF ANY
KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE
LIBRARY IS WITH YOU.  SHOULD THE LIBRARY PROVE DEFECTIVE, YOU ASSUME
THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

  16. IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN
WRITING WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY
AND/OR REDISTRIBUTE THE LIBRARY AS PERMITTED ABOVE, BE LIABLE TO YOU
FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR
CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE
LIBRARY (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING
RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A
FAILURE OF THE LIBRARY TO OPERATE WITH ANY OTHER SOFTWARE), EVEN IF
SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
DAMAGES.

		     END OF TERMS AND CONDITIONS

           How to Apply These Terms to Your New Libraries

  If you develop a new library, and you want it to be of the greatest
possible use to the public, we recommend making it free software that
everyone can redistribute and change.  You can do so by permitting
redistribution under these terms (or, alternatively, under the terms of the
ordinary General Public License).

  To apply these terms, attach the following notices to the library.  It is
safest to attach them to the start of each source file to most effectively
convey the exclusion of warranty; and each file should have at least the
"copyright" line and a pointer to where the full notice is found.

    <one line to give the library's name and a brief idea of what it does.>
    Copyright (C) <year>  <name of author>

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA

Also add information on how to contact you by electronic and paper mail.

You should also get your employer (if you work as a programmer) or your
school, if any, to sign a "copyright disclaimer" for the library, if
necessary.  Here is a sample; alter the names:

  Yoyodyne, Inc., hereby disclaims all copyright interest in the
  library `Frob' (a library for tweaking knobs) written by James Random Hacker.

  <signature of Ty Coon>, 1 April 1990
  Ty Coon, President of Vice

That's all there is to it!



<!-- /notice:32434afcc8666ba060e111d715bfdb6c2d5dd8a35fa4d3ab8ad67d8f850d2f2b -->

## Notice 3290ae0fbc9ddb77d2239121d710f0bb9d31b3b4744e6d97fe01e652b4c1870b

<!-- notice:3290ae0fbc9ddb77d2239121d710f0bb9d31b3b4744e6d97fe01e652b4c1870b -->
Short version for non-lawyers:

`linux-raw-sys` is triple-licensed under Apache 2.0 with the LLVM Exception,
Apache 2.0, and MIT terms.


Longer version:

Copyrights in the `linux-raw-sys` project are retained by their contributors.
No copyright assignment is required to contribute to the `linux-raw-sys`
project.

Some files include code derived from Rust's `libstd`; see the comments in
the code for details.

Except as otherwise noted (below and/or in individual files), `linux-raw-sys`
is licensed under:

 - the Apache License, Version 2.0, with the LLVM Exception
   <LICENSE-Apache-2.0_WITH_LLVM-exception> or
   <http://llvm.org/foundation/relicensing/LICENSE.txt>
 - the Apache License, Version 2.0
   <LICENSE-APACHE> or
   <http://www.apache.org/licenses/LICENSE-2.0>,
 - or the MIT license
   <LICENSE-MIT> or
   <http://opensource.org/licenses/MIT>,

at your option.

<!-- /notice:3290ae0fbc9ddb77d2239121d710f0bb9d31b3b4744e6d97fe01e652b4c1870b -->

## Notice 32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9

<!-- notice:32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9 -->
Copyright (c) 2017-present PyO3 Project and Contributors.  https://github.com/PyO3

                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

<!-- /notice:32c76dbe0e73d79100d5ece77c158399f2e2541bc5c78548a4ba45c1cb53c5c9 -->

## Notice 333ea3aaa3cadb819f4acd9f9153f9feee060a995ca8710f32bc5bd9a4b91734

<!-- notice:333ea3aaa3cadb819f4acd9f9153f9feee060a995ca8710f32bc5bd9a4b91734 -->
Copyright (c) 2017 The foreign-types Developers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:333ea3aaa3cadb819f4acd9f9153f9feee060a995ca8710f32bc5bd9a4b91734 -->

## Notice 334c40cc7ab76303a1555e77724200631cf31c2a3846b2602161cf8921210b46

<!-- notice:334c40cc7ab76303a1555e77724200631cf31c2a3846b2602161cf8921210b46 -->
Copyright (c) 2018 Luca Barbato

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:334c40cc7ab76303a1555e77724200631cf31c2a3846b2602161cf8921210b46 -->

## Notice 3488679340a49ecc34d342c4009d2dabf76f4a21f12aec2ca99b15805d656544

<!-- notice:3488679340a49ecc34d342c4009d2dabf76f4a21f12aec2ca99b15805d656544 -->
MIT License

Copyright (c) 2017 crc-rs Developers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:3488679340a49ecc34d342c4009d2dabf76f4a21f12aec2ca99b15805d656544 -->

## Notice 3521672491a3479422d5fe1aca6645dd2984090f85da6e5205abfb18fb7a6897

<!-- notice:3521672491a3479422d5fe1aca6645dd2984090f85da6e5205abfb18fb7a6897 -->
Copyright (c) 2021 RustCrypto Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:3521672491a3479422d5fe1aca6645dd2984090f85da6e5205abfb18fb7a6897 -->

## Notice 35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab

<!-- notice:35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab -->
                              Apache License
                        Version 2.0, January 2004
                     https://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

<!-- /notice:35242e7a83f69875e6edeff02291e688c97caafe2f8902e4e19b49d3e78b4cab -->

## Notice 377c2e7c53250cc5905c0b0532d35973392af16ffb9596a41d99d202cf3617c9

<!-- notice:377c2e7c53250cc5905c0b0532d35973392af16ffb9596a41d99d202cf3617c9 -->
Short version for non-lawyers:

`rustix` is triple-licensed under Apache 2.0 with the LLVM Exception,
Apache 2.0, and MIT terms.


Longer version:

Copyrights in the `rustix` project are retained by their contributors.
No copyright assignment is required to contribute to the `rustix`
project.

Some files include code derived from Rust's `libstd`; see the comments in
the code for details.

Except as otherwise noted (below and/or in individual files), `rustix`
is licensed under:

 - the Apache License, Version 2.0, with the LLVM Exception
   <LICENSE-Apache-2.0_WITH_LLVM-exception> or
   <http://llvm.org/foundation/relicensing/LICENSE.txt>
 - the Apache License, Version 2.0
   <LICENSE-APACHE> or
   <http://www.apache.org/licenses/LICENSE-2.0>,
 - or the MIT license
   <LICENSE-MIT> or
   <http://opensource.org/licenses/MIT>,

at your option.

<!-- /notice:377c2e7c53250cc5905c0b0532d35973392af16ffb9596a41d99d202cf3617c9 -->

## Notice 378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397

<!-- notice:378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397 -->
Copyright (c) 2014 Alex Crichton

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:378f5840b258e2779c39418f3f2d7b2ba96f1c7917dd6be0713f88305dbda397 -->

## Notice 37c1efe6301b127afb9d810c5fab62bdc60f72a7fb55f7a85ae00c0b8f6c1a42

<!-- notice:37c1efe6301b127afb9d810c5fab62bdc60f72a7fb55f7a85ae00c0b8f6c1a42 -->
MIT License

Copyright (c) 2026 PocketStation contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:37c1efe6301b127afb9d810c5fab62bdc60f72a7fb55f7a85ae00c0b8f6c1a42 -->

## Notice 391a5396cec6230bfabd4ef4eb2350eb895bc5efce377a2218f5702ed020d3e3

<!-- notice:391a5396cec6230bfabd4ef4eb2350eb895bc5efce377a2218f5702ed020d3e3 -->
Copyright (c) 2015-2025 Sean McArthur

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


<!-- /notice:391a5396cec6230bfabd4ef4eb2350eb895bc5efce377a2218f5702ed020d3e3 -->

## Notice 3cc33f8e76680b9cba2e2a5bc94de5a92420045863ab2fadbef290a55b4d8530

<!-- notice:3cc33f8e76680b9cba2e2a5bc94de5a92420045863ab2fadbef290a55b4d8530 -->
MIT License

Copyright (c) 2015-2021 David Henningsson, and other contributors.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:3cc33f8e76680b9cba2e2a5bc94de5a92420045863ab2fadbef290a55b4d8530 -->

## Notice 3f9f0f7e5a5911a8042e32c83ff5d061ce1ffd02e8a207ec2135a44ad73b4191

<!-- notice:3f9f0f7e5a5911a8042e32c83ff5d061ce1ffd02e8a207ec2135a44ad73b4191 -->
Copyright (c) 2019 Nick Fitzgerald, 2021 Yuki Okushi

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:3f9f0f7e5a5911a8042e32c83ff5d061ce1ffd02e8a207ec2135a44ad73b4191 -->

## Notice 3fa4ca83dcc9237839b1bdeb2e6d16bdfb5ec0c5ce42b24694d8bbf0dcbef72c

<!-- notice:3fa4ca83dcc9237839b1bdeb2e6d16bdfb5ec0c5ce42b24694d8bbf0dcbef72c -->
Copyright Mozilla Foundation

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:3fa4ca83dcc9237839b1bdeb2e6d16bdfb5ec0c5ce42b24694d8bbf0dcbef72c -->

## Notice 41d791701e3e1c1073470403de7e342442d1e6a2af72681023b13a2f45f2125c

<!-- notice:41d791701e3e1c1073470403de7e342442d1e6a2af72681023b13a2f45f2125c -->
/*
 * Written by Wilco Dijkstra, 1996. The following email exchange establishes the
 * license.
 *
 * From: Wilco Dijkstra <Wilco.Dijkstra@ntlworld.com>
 * Date: Fri, Jun 24, 2011 at 3:20 AM
 * Subject: Re: sqrt routine
 * To: Kevin Ma <kma@google.com>
 * Hi Kevin,
 * Thanks for asking. Those routines are public domain (originally posted to
 * comp.sys.arm a long time ago), so you can use them freely for any purpose.
 * Cheers,
 * Wilco
 *
 * ----- Original Message -----
 * From: "Kevin Ma" <kma@google.com>
 * To: <Wilco.Dijkstra@ntlworld.com>
 * Sent: Thursday, June 23, 2011 11:44 PM
 * Subject: Fwd: sqrt routine
 * Hi Wilco,
 * I saw your sqrt routine from several web sites, including
 * http://www.finesse.demon.co.uk/steven/sqrt.html.
 * Just wonder if there's any copyright information with your Successive
 * approximation routines, or if I can freely use it for any purpose.
 * Thanks.
 * Kevin
 */

<!-- /notice:41d791701e3e1c1073470403de7e342442d1e6a2af72681023b13a2f45f2125c -->

## Notice 43e358d7b6eb109d0f51f7b3a090fd82607965767c25fadee39e922475de2061

<!-- notice:43e358d7b6eb109d0f51f7b3a090fd82607965767c25fadee39e922475de2061 -->
The MIT License (MIT)

Copyright (c) 2015-2020 the fiat-crypto authors (see
https://github.com/mit-plv/fiat-crypto/blob/master/AUTHORS).

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:43e358d7b6eb109d0f51f7b3a090fd82607965767c25fadee39e922475de2061 -->

## Notice 4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1

<!-- notice:4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1 -->
The MIT License (MIT)

Copyright (c) 2015 Nicholas Allegra (comex).

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

<!-- /notice:4455bf75a91154108304cb283e0fea9948c14f13e20d60887cf2552449dea3b1 -->

## Notice 45f522cacecb1023856e46df79ca625dfc550c94910078bd8aec6e02880b3d42

<!-- notice:45f522cacecb1023856e46df79ca625dfc550c94910078bd8aec6e02880b3d42 -->
Copyright (c) 2018 Carl Lerche

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:45f522cacecb1023856e46df79ca625dfc550c94910078bd8aec6e02880b3d42 -->

## Notice 45fd05c4865e7c350b98ad7ac50e1b15462d49af4a91e9b0c9dd933dc9a69742

<!-- notice:45fd05c4865e7c350b98ad7ac50e1b15462d49af4a91e9b0c9dd933dc9a69742 -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright 2023 Dirkjan Ochtman

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:45fd05c4865e7c350b98ad7ac50e1b15462d49af4a91e9b0c9dd933dc9a69742 -->

## Notice 470355a7eed93fcc4281ec2e0f82ca3b94e7af1e4d83629f91de8cfac34d750e

<!-- notice:470355a7eed93fcc4281ec2e0f82ca3b94e7af1e4d83629f91de8cfac34d750e -->
                              Apache License
                        Version 2.0 January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:470355a7eed93fcc4281ec2e0f82ca3b94e7af1e4d83629f91de8cfac34d750e -->

## Notice 4a883ecc3bb1010faed542bf63d53e530fea5e5e12cf676aed588784298ba929

<!-- notice:4a883ecc3bb1010faed542bf63d53e530fea5e5e12cf676aed588784298ba929 -->
Copyright (c) 2021-2022 The RustCrypto Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:4a883ecc3bb1010faed542bf63d53e530fea5e5e12cf676aed588784298ba929 -->

## Notice 4cada0bd02ea3692eee6f16400d86c6508bbd3bafb2b65fed0419f36d4f83e8f

<!-- notice:4cada0bd02ea3692eee6f16400d86c6508bbd3bafb2b65fed0419f36d4f83e8f -->
Copyright (c) 2019 The CryptoCorrosion Contributors

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:4cada0bd02ea3692eee6f16400d86c6508bbd3bafb2b65fed0419f36d4f83e8f -->

## Notice 4da95ec4ecb65b738d470b7d762894ad9c97da93e6cbfb18b570fc2c96f4b871

<!-- notice:4da95ec4ecb65b738d470b7d762894ad9c97da93e6cbfb18b570fc2c96f4b871 -->
Copyright (c) Ulrik Sverdrup "bluss" 2015-2023

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:4da95ec4ecb65b738d470b7d762894ad9c97da93e6cbfb18b570fc2c96f4b871 -->

## Notice 4dbda04344456f09a7a588140455413a9ac59b6b26a1ef7cdf9c800c012d87f0

<!-- notice:4dbda04344456f09a7a588140455413a9ac59b6b26a1ef7cdf9c800c012d87f0 -->
Copyright (c) 2014-2019 Geoffroy Couprie

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<!-- /notice:4dbda04344456f09a7a588140455413a9ac59b6b26a1ef7cdf9c800c012d87f0 -->

## Notice 508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1

<!-- notice:508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1 -->
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:508a77d2e7b51d98adeed32648ad124b7b30241a8e70b2e72c99f92d8e5874d1 -->

## Notice 516b24e051bf5630880ebbd55c40a25ce9552ebaf8970a53e8976eb70e522406

<!-- notice:516b24e051bf5630880ebbd55c40a25ce9552ebaf8970a53e8976eb70e522406 -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright 2014 Paho Lurie-Gregg

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
<!-- /notice:516b24e051bf5630880ebbd55c40a25ce9552ebaf8970a53e8976eb70e522406 -->

## Notice 523a42c25d245dde9c015f882cec7f4555aad883382a6cf19b4b7d9b2cd5419b

<!-- notice:523a42c25d245dde9c015f882cec7f4555aad883382a6cf19b4b7d9b2cd5419b -->
Copyright (c) 2018-2026 The rust-random Project Developers
Copyright (c) 2014 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:523a42c25d245dde9c015f882cec7f4555aad883382a6cf19b4b7d9b2cd5419b -->

## Notice 553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583

<!-- notice:553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583 -->
Copyright 2015 Nicholas Allegra (comex).

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:553fffcd9b1cb158bc3e9edc35da85ca5c3b3d7d2e61c883ebcfa8a65814b583 -->

## Notice 55c8990ea1221b3f21cb1e603e97f8ea268cc8db082999ed59e39fc43d45fedf

<!-- notice:55c8990ea1221b3f21cb1e603e97f8ea268cc8db082999ed59e39fc43d45fedf -->
Copyright (c) 2020 Henrik Enquist

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
<!-- /notice:55c8990ea1221b3f21cb1e603e97f8ea268cc8db082999ed59e39fc43d45fedf -->

## Notice 58545fed1565e42d687aecec6897d35c6d37ccb71479a137c0deb2203e125c79

<!-- notice:58545fed1565e42d687aecec6897d35c6d37ccb71479a137c0deb2203e125c79 -->
The MIT License (MIT)

Copyright (c) 2014 Mathijs van de Nes

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:58545fed1565e42d687aecec6897d35c6d37ccb71479a137c0deb2203e125c79 -->

## Notice 5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b

<!-- notice:5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b -->
Copyright 2022 Martin Algesten

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<!-- /notice:5b460f37be48ac4cf2181596181cc6cae432fc2caae05944873f380730829a4b -->

## Notice 5c7bd92d1f096f12203dc1b601e3cb17484fa1b023e30b6b8edcc80e416237ec

<!-- notice:5c7bd92d1f096f12203dc1b601e3cb17484fa1b023e30b6b8edcc80e416237ec -->
Copyright (c) 2016-2020 RustCrypto Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:5c7bd92d1f096f12203dc1b601e3cb17484fa1b023e30b6b8edcc80e416237ec -->

## Notice 5e05b024f653a5ce199e77cbbbd42fb5553562ec714b819421ed0c3e552a75d7

<!-- notice:5e05b024f653a5ce199e77cbbbd42fb5553562ec714b819421ed0c3e552a75d7 -->
Copyright (c) 2017 Robert Grosse

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
<!-- /notice:5e05b024f653a5ce199e77cbbbd42fb5553562ec714b819421ed0c3e552a75d7 -->

## Notice 5ef8fcfb6cccec8fcae043c834099a60c8b7406408db576e026d2b7e67dc5cf5

<!-- notice:5ef8fcfb6cccec8fcae043c834099a60c8b7406408db576e026d2b7e67dc5cf5 -->
MIT License

Copyright (c) 2019 Akhil Velagapudi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:5ef8fcfb6cccec8fcae043c834099a60c8b7406408db576e026d2b7e67dc5cf5 -->

## Notice 60c93a31f490375aadf64098b75f10715010379541021e00261045d7800611d3

<!-- notice:60c93a31f490375aadf64098b75f10715010379541021e00261045d7800611d3 -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


<!-- /notice:60c93a31f490375aadf64098b75f10715010379541021e00261045d7800611d3 -->

## Notice 62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3

<!-- notice:62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3 -->
Copyright (c) 2012-2013 Mozilla Foundation

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:62065228e42caebca7e7d7db1204cbb867033de5982ca4009928915e4095f3a3 -->

## Notice 62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a

<!-- notice:62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

<!-- /notice:62c7a1e35f56406896d7aa7ca52d0cc0d272ac022b5d2796e7d6905db8a3636a -->

## Notice 63af4bea227c94d021e99427f6ca3a4b8efddadcca93ab6130f708cf6138cf68

<!-- notice:63af4bea227c94d021e99427f6ca3a4b8efddadcca93ab6130f708cf6138cf68 -->
Copyright (c) 2018-2022 RustCrypto Developers
Copyright (c) 2018 Artyom Pavlov

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:63af4bea227c94d021e99427f6ca3a4b8efddadcca93ab6130f708cf6138cf68 -->

## Notice 6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb

<!-- notice:6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb -->
Copyright (c) 2014 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:6485b8ed310d3f0340bf1ad1f47645069ce4069dcc6bb46c7d5c6faf41de1fdb -->

## Notice 65f94e99ddaf4f5d1782a6dae23f35d4293a9a01444a13135a6887017d353cee

<!-- notice:65f94e99ddaf4f5d1782a6dae23f35d4293a9a01444a13135a6887017d353cee -->
Copyright (c) 2019 Nick Fitzgerald

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:65f94e99ddaf4f5d1782a6dae23f35d4293a9a01444a13135a6887017d353cee -->

## Notice 6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd

<!-- notice:6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd -->
Copyright (c) 2016 Alex Crichton
Copyright (c) 2017 The Tokio Authors

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:6652c868f35dfe5e8ef636810a4e576b9d663f3a17fb0f5613ad73583e1b88fd -->

## Notice 6b3b465fa69075348ee5ffc9ba6afa93402743a4a942a463404fac25257bd3ed

<!-- notice:6b3b465fa69075348ee5ffc9ba6afa93402743a4a942a463404fac25257bd3ed -->
Copyright (c) 2016 Tad Hardesty

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

<!-- /notice:6b3b465fa69075348ee5ffc9ba6afa93402743a4a942a463404fac25257bd3ed -->

## Notice 6db9d4840c6ff0fb3c37ace8e32cfd3eb6c6e759c67b4ecbee969cd8d75154a9

<!-- notice:6db9d4840c6ff0fb3c37ace8e32cfd3eb6c6e759c67b4ecbee969cd8d75154a9 -->
Copyright (c) 2011, Google Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in
    the documentation and/or other materials provided with the
    distribution.

  * Neither the name of Google nor the names of its contributors may
    be used to endorse or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 

<!-- /notice:6db9d4840c6ff0fb3c37ace8e32cfd3eb6c6e759c67b4ecbee969cd8d75154a9 -->

## Notice 6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51

<!-- notice:6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51 -->
                              Apache License
                        Version 2.0, January 2004
                     https://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

<!-- /notice:6df43f6f4b5d4587f3d8d71e45532c688fd168afa5fe89d571cb32fa09c4ef51 -->

## Notice 6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6

<!-- notice:6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6 -->
Copyright (c) Individual contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:6efb0476a1cc085077ed49357026d8c173bf33017278ef440f222fb9cbcb66e6 -->

## Notice 6fdbabd2c95c5efc6f1e46175278239afb9343120a3022ed0e0cb04267a6aeb3

<!-- notice:6fdbabd2c95c5efc6f1e46175278239afb9343120a3022ed0e0cb04267a6aeb3 -->
/*
 * Copyright(c)1995,97 Mark Olesen <olesen@me.QueensU.CA>
 *    Queen's Univ at Kingston (Canada)
 *
 * Permission to use, copy, modify, and distribute this software for
 * any purpose without fee is hereby granted, provided that this
 * entire notice is included in all copies of any software which is
 * or includes a copy or modification of this software and in all
 * copies of the supporting documentation for such software.
 *
 * THIS SOFTWARE IS BEING PROVIDED "AS IS", WITHOUT ANY EXPRESS OR
 * IMPLIED WARRANTY.  IN PARTICULAR, NEITHER THE AUTHOR NOR QUEEN'S
 * UNIVERSITY AT KINGSTON MAKES ANY REPRESENTATION OR WARRANTY OF ANY
 * KIND CONCERNING THE MERCHANTABILITY OF THIS SOFTWARE OR ITS
 * FITNESS FOR ANY PARTICULAR PURPOSE.
 *
 * All of which is to say that you can do what you like with this
 * source code provided you don't try to sell it as your own and you
 * include an unaltered copy of this message (including the
 * copyright).
 *
 * It is also implicitly understood that bug fixes and improvements
 * should make their way back to the general Internet community so
 * that everyone benefits.
 */

<!-- /notice:6fdbabd2c95c5efc6f1e46175278239afb9343120a3022ed0e0cb04267a6aeb3 -->

## Notice 728536b4160e051f86d7c9c388f704866b3d512cd7df97ac3516c65279523c4e

<!-- notice:728536b4160e051f86d7c9c388f704866b3d512cd7df97ac3516c65279523c4e -->
AWS Libcrypto (AWS-LC)

AWS-LC is a fork of BoringSSL, which is itself a fork of OpenSSL.
Content from these and other sources retains their original licensing,
as described below. New files from AWS-LC are made available under the Apache-2.0 license OR the ISC
license. These licenses are reproduced at the bottom of this file.

```
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0 OR ISC
```


================================================================================
BoringSSL
================================================================================

BoringSSL is a Google-maintained fork of OpenSSL. Historically, code
authored by Google for BoringSSL was licensed under the ISC License.
BoringSSL has since relicensed upstream to Apache License 2.0. Existing
AWS-LC code originating from BoringSSL retains its ISC license, while
newer code taken from BoringSSL is licensed under Apache License 2.0.

```
Copyright (c) 2014-2024 Google Inc.
SPDX-License-Identifier: ISC
```

Additional individual contributions to BoringSSL-derived code are
covered under the ISC license:

  - Brian Smith (Copyright 2016)
  - Robert Nagy (Copyright 2022)
  - Arm Ltd (Copyright 2020)

```
Copyright (c) 2025-2026 Google Inc.
SPDX-License-Identifier: Apache-2.0
```

================================================================================
OpenSSL
================================================================================

Code derived from the OpenSSL project is licensed under the
Apache License, Version 2.0.

```
Copyright (c) 1998-2011 The OpenSSL Project. All rights reserved.
SPDX-License-Identifier: Apache-2.0
```

Some OpenSSL-derived files also carry the original SSLeay copyright:

```
Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com). All rights reserved.
SPDX-License-Identifier: Apache-2.0
```

Portions of OpenSSL-derived code include contributions from:

  - Sun Microsystems, Inc. (Copyright 2002)
  - Nokia (Copyright 2005)
  - Intel Corporation (Copyright 2012-2021)

These contributions are covered under the Apache-2.0 license.

================================================================================
mlkem-native
================================================================================

Code from the mlkem-native project is licensed under Apache License 2.0 or MIT or ISC.

```
Copyright (c) The mlkem-native project authors.
SPDX-License-Identifier: Apache-2.0 OR ISC OR MIT
```

================================================================================
mldsa-native
================================================================================

Code from the mldsa-native project is licensed under Apache License 2.0 or MIT or ISC

```
Copyright (c) The mldsa-native project authors.
SPDX-License-Identifier: Apache-2.0 OR ISC OR MIT
```

================================================================================
Third-Party Libraries (compiled into libcrypto/libssl)
================================================================================

Fiat Cryptography
-----------------
Synthesizing Correct-by-Construction Code for Cryptographic Primitives.
See third_party/fiat/LICENSE.

```
Copyright (c) 2015-2020 the fiat-crypto authors.
SPDX-License-Identifier: MIT
```

s2n-bignum
----------
Integer arithmetic routines for cryptography.
See third_party/s2n-bignum/s2n-bignum-imported/LICENSE.

```
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0 OR ISC OR MIT-0
```

Note: ML-KEM/SHA3 code within s2n-bignum is licensed as
Apache-2.0 OR ISC OR MIT (with attribution), sourced from the
mlkem-native project.

Jitter Entropy RNG
-------------------
CPU Jitter Random Number Generator Library.
See third_party/jitterentropy/jitterentropy-library/LICENSE.

The Jitter Entropy library is dual-licensed under a BSD-style license
and the GNU General Public License Version 2. Amazon expressly elects
to distribute the package under the 3-Clause BSD License and NOT under
GNU General Public License Version 2.

```
Copyright (C) 2017 - 2025, Stephan Mueller <smueller@chronox.de>.
SPDX-License-Identifier: BSD-3-Clause
```

Keccak / AES Reference Implementations
---------------------------------------
Public domain (CC0) contributions.
https://creativecommons.org/public-domain/cc0

Code from sources and by authors listed in comments on top of the respective files.


================================================================================
Third-Party Libraries (NOT compiled into libcrypto/libssl)
================================================================================

The following are used for testing and build tooling only. Distributing
code linked against AWS-LC (libcrypto/libssl) does NOT trigger these
license obligations.

Google Test
-----------
See third_party/googletest/LICENSE.

```
Copyright 2008 Google Inc.
SPDX-License-Identifier: BSD-3-Clause
```

Go Standard Library
-------------------
Code in ssl/test/runner/ is derived from the Go standard library.

```
Copyright (c) The Go Authors. All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
```

Wycheproof Test Vectors
------------------------
Project Wycheproof is a community managed repository of test vectors that can be used by cryptography library
developers to test against known attacks, specification inconsistencies, and other various implementation bugs.

See third_party/wycheproof_testvectors/LICENSE.

```
SPDX-License-Identifier: Apache-2.0
```


================================================================================
Full License Texts
================================================================================

Apache License 2.0
------------------
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

    1. Definitions.

        "License" shall mean the terms and conditions for use, reproduction, and distribution as defined by Sections 1 through 9 of this document.

        "Licensor" shall mean the copyright owner or entity authorized by the copyright owner that is granting the License.

        "Legal Entity" shall mean the union of the acting entity and all other entities that control, are controlled by, or are under common control with that entity. For the purposes of this definition, "control" means (i) the power, direct or indirect, to cause the direction or management of such entity, whether by contract or otherwise, or (ii) ownership of fifty percent (50%) or more of the outstanding shares, or (iii) beneficial ownership of such entity.

        "You" (or "Your") shall mean an individual or Legal Entity exercising permissions granted by this License.

        "Source" form shall mean the preferred form for making modifications, including but not limited to software source code, documentation source, and configuration files.

        "Object" form shall mean any form resulting from mechanical transformation or translation of a Source form, including but not limited to compiled object code, generated documentation, and conversions to other media types.

        "Work" shall mean the work of authorship, whether in Source or Object form, made available under the License, as indicated by a copyright notice that is included in or attached to the work (an example is provided in the Appendix below).

        "Derivative Works" shall mean any work, whether in Source or Object form, that is based on (or derived from) the Work and for which the editorial revisions, annotations, elaborations, or other modifications represent, as a whole, an original work of authorship. For the purposes of this License, Derivative Works shall not include works that remain separable from, or merely link (or bind by name) to the interfaces of, the Work and Derivative Works thereof.

        "Contribution" shall mean any work of authorship, including the original version of the Work and any modifications or additions to that Work or Derivative Works thereof, that is intentionally submitted to Licensor for inclusion in the Work by the copyright owner or by an individual or Legal Entity authorized to submit on behalf of the copyright owner. For the purposes of this definition, "submitted" means any form of electronic, verbal, or written communication sent to the Licensor or its representatives, including but not limited to communication on electronic mailing lists, source code control systems, and issue tracking systems that are managed by, or on behalf of, the Licensor for the purpose of discussing and improving the Work, but excluding communication that is conspicuously marked or otherwise designated in writing by the copyright owner as "Not a Contribution."

        "Contributor" shall mean Licensor and any individual or Legal Entity on behalf of whom a Contribution has been received by Licensor and subsequently incorporated within the Work.
    2. Grant of Copyright License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare Derivative Works of, publicly display, publicly perform, sublicense, and distribute the Work and such Derivative Works in Source or Object form.
    3. Grant of Patent License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable (except as stated in this section) patent license to make, have made, use, offer to sell, sell, import, and otherwise transfer the Work, where such license applies only to those patent claims licensable by such Contributor that are necessarily infringed by their Contribution(s) alone or by combination of their Contribution(s) with the Work to which such Contribution(s) was submitted. If You institute patent litigation against any entity (including a cross-claim or counterclaim in a lawsuit) alleging that the Work or a Contribution incorporated within the Work constitutes direct or contributory patent infringement, then any patent licenses granted to You under this License for that Work shall terminate as of the date such litigation is filed.
    4. Redistribution. You may reproduce and distribute copies of the Work or Derivative Works thereof in any medium, with or without modifications, and in Source or Object form, provided that You meet the following conditions:
        (a) You must give any other recipients of the Work or Derivative Works a copy of this License; and
        (b) You must cause any modified files to carry prominent notices stating that You changed the files; and
        (c) You must retain, in the Source form of any Derivative Works that You distribute, all copyright, patent, trademark, and attribution notices from the Source form of the Work, excluding those notices that do not pertain to any part of the Derivative Works; and
        (d) If the Work includes a "NOTICE" text file as part of its distribution, then any Derivative Works that You distribute must include a readable copy of the attribution notices contained within such NOTICE file, excluding those notices that do not pertain to any part of the Derivative Works, in at least one of the following places: within a NOTICE text file distributed as part of the Derivative Works; within the Source form or documentation, if provided along with the Derivative Works; or, within a display generated by the Derivative Works, if and wherever such third-party notices normally appear. The contents of the NOTICE file are for informational purposes only and do not modify the License. You may add Your own attribution notices within Derivative Works that You distribute, alongside or as an addendum to the NOTICE text from the Work, provided that such additional attribution notices cannot be construed as modifying the License.

    You may add Your own copyright statement to Your modifications and may provide additional or different license terms and conditions for use, reproduction, or distribution of Your modifications, or for any such Derivative Works as a whole, provided Your use, reproduction, and distribution of the Work otherwise complies with the conditions stated in this License.
    5. Submission of Contributions. Unless You explicitly state otherwise, any Contribution intentionally submitted for inclusion in the Work by You to the Licensor shall be under the terms and conditions of this License, without any additional terms or conditions. Notwithstanding the above, nothing herein shall supersede or modify the terms of any separate license agreement you may have executed with Licensor regarding such Contributions.
    6. Trademarks. This License does not grant permission to use the trade names, trademarks, service marks, or product names of the Licensor, except as required for reasonable and customary use in describing the origin of the Work and reproducing the content of the NOTICE file.
    7. Disclaimer of Warranty. Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE. You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with Your exercise of permissions under this License.
    8. Limitation of Liability. In no event and under no legal theory, whether in tort (including negligence), contract, or otherwise, unless required by applicable law (such as deliberate and grossly negligent acts) or agreed to in writing, shall any Contributor be liable to You for damages, including any direct, indirect, special, incidental, or consequential damages of any character arising as a result of this License or out of the use or inability to use the Work (including but not limited to damages for loss of goodwill, work stoppage, computer failure or malfunction, or any and all other commercial damages or losses), even if such Contributor has been advised of the possibility of such damages.
    9. Accepting Warranty or Additional Liability. While redistributing the Work or Derivative Works thereof, You may choose to offer, and charge a fee for, acceptance of support, warranty, indemnity, or other liability obligations and/or rights consistent with this License. However, in accepting such obligations, You may act only on Your own behalf and on Your sole responsibility, not on behalf of any other Contributor, and only if You agree to indemnify, defend, and hold each Contributor harmless for any liability incurred by, or claims asserted against, such Contributor by reason of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

To apply the Apache License to your work, attach the following boilerplate notice, with the fields enclosed by brackets "[]" replaced with your own identifying information. (Don't include the brackets!) The text should be enclosed in the appropriate comment syntax for the file format. We also recommend that a file or class name and description of purpose be included on the same "printed page" as the copyright notice for easier identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

ISC License
-----------
Permission to use, copy, modify, and/or distribute this software for
any purpose with or without fee is hereby granted, provided that the
above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.

MIT License
-----------
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

BSD 3-Clause License
--------------------
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived
   from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

MIT No Attribution (MIT-0)
--------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<!-- /notice:728536b4160e051f86d7c9c388f704866b3d512cd7df97ac3516c65279523c4e -->

## Notice 7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349

<!-- notice:7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349 -->
Copyright (c) 2016--2023

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:7365cc8878a1d7ce155a58c4ca09c3d7a6be413efa5334a80ea842912b669349 -->

## Notice 74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3

<!-- notice:74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3 -->
UNICODE, INC. LICENSE AGREEMENT - DATA FILES AND SOFTWARE

Unicode Data Files include all data files under the directories
http://www.unicode.org/Public/, http://www.unicode.org/reports/,
http://www.unicode.org/cldr/data/, http://source.icu-project.org/repos/icu/, and
http://www.unicode.org/utility/trac/browser/.

Unicode Data Files do not include PDF online code charts under the
directory http://www.unicode.org/Public/.

Software includes any source code published in the Unicode Standard
or under the directories
http://www.unicode.org/Public/, http://www.unicode.org/reports/,
http://www.unicode.org/cldr/data/, http://source.icu-project.org/repos/icu/, and
http://www.unicode.org/utility/trac/browser/.

NOTICE TO USER: Carefully read the following legal agreement.
BY DOWNLOADING, INSTALLING, COPYING OR OTHERWISE USING UNICODE INC.'S
DATA FILES ("DATA FILES"), AND/OR SOFTWARE ("SOFTWARE"),
YOU UNEQUIVOCALLY ACCEPT, AND AGREE TO BE BOUND BY, ALL OF THE
TERMS AND CONDITIONS OF THIS AGREEMENT.
IF YOU DO NOT AGREE, DO NOT DOWNLOAD, INSTALL, COPY, DISTRIBUTE OR USE
THE DATA FILES OR SOFTWARE.

COPYRIGHT AND PERMISSION NOTICE

Copyright © 1991-2018 Unicode, Inc. All rights reserved.
Distributed under the Terms of Use in http://www.unicode.org/copyright.html.

Permission is hereby granted, free of charge, to any person obtaining
a copy of the Unicode data files and any associated documentation
(the "Data Files") or Unicode software and any associated documentation
(the "Software") to deal in the Data Files or Software
without restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, and/or sell copies of
the Data Files or Software, and to permit persons to whom the Data Files
or Software are furnished to do so, provided that either
(a) this copyright and permission notice appear with all copies
of the Data Files or Software, or
(b) this copyright and permission notice appear in associated
Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT OF THIRD PARTY RIGHTS.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS
NOTICE BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL
DAMAGES, OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE,
DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THE DATA FILES OR SOFTWARE.

Except as contained in this notice, the name of a copyright holder
shall not be used in advertising or otherwise to promote the sale,
use or other dealings in these Data Files or Software without prior
written authorization of the copyright holder.

<!-- /notice:74db5baf44a41b1000312c673544b3374e4198af5605c7f9080a402cec42cfa3 -->

## Notice 756c8d2ab2dc24f256e1455b5f03937f4933d83d7bc9f2d55009fc962377d512

<!-- notice:756c8d2ab2dc24f256e1455b5f03937f4933d83d7bc9f2d55009fc962377d512 -->
Copyright 2016 RustAudio Developers

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:756c8d2ab2dc24f256e1455b5f03937f4933d83d7bc9f2d55009fc962377d512 -->

## Notice 7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545

<!-- notice:7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545 -->
Copyright (c) 2015

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:7576269ea71f767b99297934c0b2367532690f8c4badc695edf8e04ab6a1e545 -->

## Notice 7a6631daa22a9f1772e4a474ede9c3374a6c7a89b61c8b5973f7fd5ccd5cee8c

<!-- notice:7a6631daa22a9f1772e4a474ede9c3374a6c7a89b61c8b5973f7fd5ccd5cee8c -->
MIT License

Copyright (c) 2021-2026 WebRTC.rs
Copyright (c) 2026 Martin Algesten

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:7a6631daa22a9f1772e4a474ede9c3374a6c7a89b61c8b5973f7fd5ccd5cee8c -->

## Notice 7abd9b6960dcf7d4d0a48606a5b71bfe37d472db68d70637f3a58a56785f1621

<!-- notice:7abd9b6960dcf7d4d0a48606a5b71bfe37d472db68d70637f3a58a56785f1621 -->
// Copyright 2015-2016 Brian Smith.
//
// Permission to use, copy, modify, and/or distribute this software for any
// purpose with or without fee is hereby granted, provided that the above
// copyright notice and this permission notice appear in all copies.
//
// THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHORS DISCLAIM ALL WARRANTIES
// WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
// MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR
// ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
// WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
// ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
// OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

<!-- /notice:7abd9b6960dcf7d4d0a48606a5b71bfe37d472db68d70637f3a58a56785f1621 -->

## Notice 7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0

<!-- notice:7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0 -->
Copyright (c) 2015 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:7b63ecd5f1902af1b63729947373683c32745c16a10e8e6292e2e2dcd7e90ae0 -->

## Notice 7d5450cb2d142651b8afa315b5f238efc805dad827d91ba367d8516bc9d49e7a

<!-- notice:7d5450cb2d142651b8afa315b5f238efc805dad827d91ba367d8516bc9d49e7a -->

                                 Apache License
                           Version 2.0, January 2004
                        https://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

<!-- /notice:7d5450cb2d142651b8afa315b5f238efc805dad827d91ba367d8516bc9d49e7a -->

## Notice 7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54

<!-- notice:7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54 -->
# License

The licensing of these crates is a bit complicated:
- The crates `objc2`, `block2`, `objc2-foundation` and `objc2-encode` are
  [currently][#23] licensed under [the MIT license][MIT].
- All other crates are trio-licensed under the [Zlib], [Apache-2.0] or [MIT]
  license, at your option.

Furthermore, the crates are (usually automatically) derived from Apple SDKs,
and that may have implications for licensing, see below for details.

[#23]: https://github.com/madsmtm/objc2/issues/23
[MIT]: https://opensource.org/license/MIT
[Zlib]: https://zlib.net/zlib_license.html
[Apache-2.0]: https://www.apache.org/licenses/LICENSE-2.0


## Apple SDKs

These crates are derived from Apple SDKs shipped with Xcode. You can obtain a
copy of the Xcode license at:

https://www.apple.com/legal/sla/docs/xcode.pdf

Or by typing `xcodebuild -license` in your terminal.

From reading the license, it is unclear whether distributing derived works
such as these crates are allowed?

But in any case, to practically use these crates, you will have to link, and
that only works when you have the correct Xcode SDK available to provide the
required `.tbd` files, which is why we choose to still use the normal SPDX
identifiers in the crates (Xcode is required to use the crates, and when using
Xcode you have already agreed to the Xcode license).

<!-- /notice:7f976f7e9cb2d87df7230606feb932c3f21ac0e664045a775b600046ff850c54 -->

## Notice 7fea0ee51a4ca5d5cea7464135fd55e8b09caf3a61da3d451ac8a22af95c033f

<!-- notice:7fea0ee51a4ca5d5cea7464135fd55e8b09caf3a61da3d451ac8a22af95c033f -->
Copyright (c) 2017 Alexey Galakhov
Copyright (c) 2016 Jason Housley

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

<!-- /notice:7fea0ee51a4ca5d5cea7464135fd55e8b09caf3a61da3d451ac8a22af95c033f -->

## Notice 814d11eba59f964bca7e74ef94f0d1eff1d5f322f895fb9b5d7e06f77debf3b2

<!-- notice:814d11eba59f964bca7e74ef94f0d1eff1d5f322f895fb9b5d7e06f77debf3b2 -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright (c) 2021-2026 WebRTC.rs
Copyright (c) 2026 Martin Algesten

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:814d11eba59f964bca7e74ef94f0d1eff1d5f322f895fb9b5d7e06f77debf3b2 -->

## Notice 8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90

<!-- notice:8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90 -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:8173d5c29b4f956d532781d2b86e4e30f83e6b7878dce18c919451d6ba707c90 -->

## Notice 83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32

<!-- notice:83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32 -->
Copyright 2019 The Fuchsia Authors.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

   * Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above
copyright notice, this list of conditions and the following disclaimer
in the documentation and/or other materials provided with the
distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

<!-- /notice:83c1763356e822adde0a2cae748d938a73fdc263849ccff6b27776dff213bd32 -->

## Notice 8764a597675778ddfd4e25f81b08a05dbcf089ac05662df7613fe67f150e3aa2

<!-- notice:8764a597675778ddfd4e25f81b08a05dbcf089ac05662df7613fe67f150e3aa2 -->
Copyright (c) 2014 Chris Wong

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:8764a597675778ddfd4e25f81b08a05dbcf089ac05662df7613fe67f150e3aa2 -->

## Notice 8909c319a7e27dbb33a15b9035f89ab3b7b2f6a12f8bcddc755206a8db1ada44

<!-- notice:8909c319a7e27dbb33a15b9035f89ab3b7b2f6a12f8bcddc755206a8db1ada44 -->
Copyright © 2018 Wim Taymans

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice (including the next
paragraph) shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

---

The above is the version of the MIT "Expat" License used by X.org:

    http://cgit.freedesktop.org/xorg/xserver/tree/COPYING

<!-- /notice:8909c319a7e27dbb33a15b9035f89ab3b7b2f6a12f8bcddc755206a8db1ada44 -->

## Notice 898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1

<!-- notice:898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1 -->
Copyright (c) 2019 Tokio Contributors

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:898b1ae9821e98daf8964c8d6c7f61641f5f5aa78ad500020771c0939ee0dea1 -->

## Notice 8ada45cd9f843acf64e4722ae262c622a2b3b3007c7310ef36ac1061a30f6adb

<!-- notice:8ada45cd9f843acf64e4722ae262c622a2b3b3007c7310ef36ac1061a30f6adb -->
                              Apache License
                        Version 2.0, January 2004
                     https://www.apache.org/licenses/LICENSE-2.0

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:8ada45cd9f843acf64e4722ae262c622a2b3b3007c7310ef36ac1061a30f6adb -->

## Notice 8b427f5bc501764575e52ba4f9d95673cf8f6d80a86d0d06599852e1a9a20a36

<!-- notice:8b427f5bc501764575e52ba4f9d95673cf8f6d80a86d0d06599852e1a9a20a36 -->
Copyright (c) 2015 Steven Allen

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:8b427f5bc501764575e52ba4f9d95673cf8f6d80a86d0d06599852e1a9a20a36 -->

## Notice 8b43ce8accd61e9d370b5ca9e9c4f953279b5c239926c62315b40e24df51b726

<!-- notice:8b43ce8accd61e9d370b5ca9e9c4f953279b5c239926c62315b40e24df51b726 -->
Copyright (c) The rust-url developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:8b43ce8accd61e9d370b5ca9e9c4f953279b5c239926c62315b40e24df51b726 -->

## Notice 8bb1b50b0e5c9399ae33bd35fab2769010fa6c14e8860c729a52295d84896b7a

<!-- notice:8bb1b50b0e5c9399ae33bd35fab2769010fa6c14e8860c729a52295d84896b7a -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright 2017 http-rs authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:8bb1b50b0e5c9399ae33bd35fab2769010fa6c14e8860c729a52295d84896b7a -->

## Notice 8c7516d4b27b1e495be5e38b612298b63de48d05f49cdac94f70f3cd70f8864b

<!-- notice:8c7516d4b27b1e495be5e38b612298b63de48d05f49cdac94f70f3cd70f8864b -->
Copyright (c) 2018-2026 The RustCrypto Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:8c7516d4b27b1e495be5e38b612298b63de48d05f49cdac94f70f3cd70f8864b -->

## Notice 8ce0830173fdac609dfb4ea603fdc002c2f4af0dc9b1a005653f5da9cf534b18

<!-- notice:8ce0830173fdac609dfb4ea603fdc002c2f4af0dc9b1a005653f5da9cf534b18 -->
Copyright (c) 2019 Carl Lerche

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:8ce0830173fdac609dfb4ea603fdc002c2f4af0dc9b1a005653f5da9cf534b18 -->

## Notice 904801faf3f1850328af8e1aa1047b9190cc22ed40df5c87f2d93d17f847ef67

<!-- notice:904801faf3f1850328af8e1aa1047b9190cc22ed40df5c87f2d93d17f847ef67 -->
Copyright (c) 2020 The RustCrypto Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:904801faf3f1850328af8e1aa1047b9190cc22ed40df5c87f2d93d17f847ef67 -->

## Notice 90c503b61dee04e1449c323ec34c229dfb68d7adcb96c7e140ee55f70fce2d8e

<!-- notice:90c503b61dee04e1449c323ec34c229dfb68d7adcb96c7e140ee55f70fce2d8e -->
Copyright (c) 2021 The RustCrypto Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:90c503b61dee04e1449c323ec34c229dfb68d7adcb96c7e140ee55f70fce2d8e -->

## Notice 90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5

<!-- notice:90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5 -->
Copyrights in the Rand project are retained by their contributors. No
copyright assignment is required to contribute to the Rand project.

For full authorship information, see the version control history.

Except as otherwise noted (below and/or in individual files), Rand is
licensed under the Apache License, Version 2.0 <LICENSE-APACHE> or
<http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
<LICENSE-MIT> or <http://opensource.org/licenses/MIT>, at your option.

The Rand project includes code from the Rust project
published under these same licenses.

<!-- /notice:90eb64f0279b0d9432accfa6023ff803bc4965212383697eee27a0f426d5f8d5 -->

## Notice 9117d922e667125508dde62b02c1f57ed22f5ad21eb536aa2e2d99e1c796e639

<!-- notice:9117d922e667125508dde62b02c1f57ed22f5ad21eb536aa2e2d99e1c796e639 -->
Copyright (c) 2023 Dirkjan Ochtman <dirkjan@ochtman.nl>

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:9117d922e667125508dde62b02c1f57ed22f5ad21eb536aa2e2d99e1c796e639 -->

## Notice 91e934255ba3b2f21103d68c5581c23ef34aa95c4628e4405b8c901935e11c69

<!-- notice:91e934255ba3b2f21103d68c5581c23ef34aa95c4628e4405b8c901935e11c69 -->
The MIT License (MIT)

Copyright (c) 2015 Steven Fackler

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<!-- /notice:91e934255ba3b2f21103d68c5581c23ef34aa95c4628e4405b8c901935e11c69 -->

## Notice 949ab7b3e7140fee216f06fe3a2bd67d68dd511f8ea73c1e01c98cb348e9c8ae

<!-- notice:949ab7b3e7140fee216f06fe3a2bd67d68dd511f8ea73c1e01c98cb348e9c8ae -->
Copyright (c) 2019 The RustCrypto Project Developers
Copyright (c) 2019 MobileCoin, LLC

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:949ab7b3e7140fee216f06fe3a2bd67d68dd511f8ea73c1e01c98cb348e9c8ae -->

## Notice 95bd3988beee069fa2848f648dab43cc6e0b2add2ad6bcb17360caf749802bcc

<!-- notice:95bd3988beee069fa2848f648dab43cc6e0b2add2ad6bcb17360caf749802bcc -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS
<!-- /notice:95bd3988beee069fa2848f648dab43cc6e0b2add2ad6bcb17360caf749802bcc -->

## Notice 977c541bd25ffe36975dde25c028c0cd15ddf3d08243983b58e8a6a3d9447523

<!-- notice:977c541bd25ffe36975dde25c028c0cd15ddf3d08243983b58e8a6a3d9447523 -->
AWS Libcrypto (AWS-LC)

AWS-LC is a fork of BoringSSL, which is itself a fork of OpenSSL.
Content from these and other sources retains their original licensing,
as described below. New files from AWS-LC are made available under the Apache-2.0 license OR the ISC
license. These licenses are reproduced at the bottom of this file.

```
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0 OR ISC
```


================================================================================
BoringSSL
================================================================================

BoringSSL is a Google-maintained fork of OpenSSL. Historically, code
authored by Google for BoringSSL was licensed under the ISC License.
BoringSSL has since relicensed upstream to Apache License 2.0. Existing
AWS-LC code originating from BoringSSL retains its ISC license, while
newer code taken from BoringSSL is licensed under Apache License 2.0.

```
Copyright (c) 2014-2024 Google Inc.
SPDX-License-Identifier: ISC
```

Additional individual contributions to BoringSSL-derived code are
covered under the ISC license:

  - Brian Smith (Copyright 2016)
  - Robert Nagy (Copyright 2022)
  - Arm Ltd (Copyright 2020)

```
Copyright (c) 2025-2026 Google Inc.
SPDX-License-Identifier: Apache-2.0
```

================================================================================
OpenSSL
================================================================================

Code derived from the OpenSSL project is licensed under the
Apache License, Version 2.0.

```
Copyright (c) 1998-2011 The OpenSSL Project. All rights reserved.
SPDX-License-Identifier: Apache-2.0
```

Some OpenSSL-derived files also carry the original SSLeay copyright:

```
Copyright (c) 1995-1998 Eric Young (eay@cryptsoft.com). All rights reserved.
SPDX-License-Identifier: Apache-2.0
```

Portions of OpenSSL-derived code include contributions from:

  - Sun Microsystems, Inc. (Copyright 2002)
  - Nokia (Copyright 2005)
  - Intel Corporation (Copyright 2012-2021)

These contributions are covered under the Apache-2.0 license.

================================================================================
mlkem-native
================================================================================

Code from the mlkem-native project is licensed under Apache License 2.0 or MIT or ISC.

```
Copyright (c) The mlkem-native project authors.
SPDX-License-Identifier: Apache-2.0 OR ISC OR MIT
```

================================================================================
mldsa-native
================================================================================

Code from the mldsa-native project is licensed under Apache License 2.0 or MIT or ISC

```
Copyright (c) The mldsa-native project authors.
SPDX-License-Identifier: Apache-2.0 OR ISC OR MIT
```

================================================================================
Third-Party Libraries (compiled into libcrypto/libssl)
================================================================================

Fiat Cryptography
-----------------
Synthesizing Correct-by-Construction Code for Cryptographic Primitives.
See third_party/fiat/LICENSE.

```
Copyright (c) 2015-2020 the fiat-crypto authors.
SPDX-License-Identifier: MIT
```

s2n-bignum
----------
Integer arithmetic routines for cryptography.
See third_party/s2n-bignum/s2n-bignum-imported/LICENSE.

```
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: Apache-2.0 OR ISC OR MIT-0
```

Note: ML-KEM/SHA3 code within s2n-bignum is licensed as
Apache-2.0 OR ISC OR MIT (with attribution), sourced from the
mlkem-native project.

Jitter Entropy RNG
-------------------
CPU Jitter Random Number Generator Library.
See third_party/jitterentropy/jitterentropy-library/LICENSE.

The Jitter Entropy library is dual-licensed under a BSD-style license
and the GNU General Public License Version 2. Amazon expressly elects
to distribute the package under the 3-Clause BSD License and NOT under
GNU General Public License Version 2.

```
Copyright (C) 2017 - 2025, Stephan Mueller <smueller@chronox.de>.
SPDX-License-Identifier: BSD-3-Clause
```

Keccak / AES Reference Implementations
---------------------------------------
Public domain (CC0) contributions.
https://creativecommons.org/public-domain/cc0

Code from sources and by authors listed in comments on top of the respective files.


================================================================================
Third-Party Libraries (NOT compiled into libcrypto/libssl)
================================================================================

The following are used for testing and build tooling only. Distributing
code linked against AWS-LC (libcrypto/libssl) does NOT trigger these
license obligations.

Google Test
-----------
See third_party/googletest/LICENSE.

```
Copyright 2008 Google Inc.
SPDX-License-Identifier: BSD-3-Clause
```

Go Standard Library
-------------------
Code in ssl/test/runner/ is derived from the Go standard library.

```
Copyright (c) The Go Authors. All rights reserved.
SPDX-License-Identifier: BSD-3-Clause
```

Wycheproof Test Vectors
------------------------
Project Wycheproof is a community managed repository of test vectors that can be used by cryptography library
developers to test against known attacks, specification inconsistencies, and other various implementation bugs.

See third_party/wycheproof_testvectors/LICENSE.

```
SPDX-License-Identifier: Apache-2.0
```


================================================================================
Full License Texts
================================================================================

Apache License 2.0
------------------
Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

    1. Definitions.

        "License" shall mean the terms and conditions for use, reproduction, and distribution as defined by Sections 1 through 9 of this document.

        "Licensor" shall mean the copyright owner or entity authorized by the copyright owner that is granting the License.

        "Legal Entity" shall mean the union of the acting entity and all other entities that control, are controlled by, or are under common control with that entity. For the purposes of this definition, "control" means (i) the power, direct or indirect, to cause the direction or management of such entity, whether by contract or otherwise, or (ii) ownership of fifty percent (50%) or more of the outstanding shares, or (iii) beneficial ownership of such entity.

        "You" (or "Your") shall mean an individual or Legal Entity exercising permissions granted by this License.

        "Source" form shall mean the preferred form for making modifications, including but not limited to software source code, documentation source, and configuration files.

        "Object" form shall mean any form resulting from mechanical transformation or translation of a Source form, including but not limited to compiled object code, generated documentation, and conversions to other media types.

        "Work" shall mean the work of authorship, whether in Source or Object form, made available under the License, as indicated by a copyright notice that is included in or attached to the work (an example is provided in the Appendix below).

        "Derivative Works" shall mean any work, whether in Source or Object form, that is based on (or derived from) the Work and for which the editorial revisions, annotations, elaborations, or other modifications represent, as a whole, an original work of authorship. For the purposes of this License, Derivative Works shall not include works that remain separable from, or merely link (or bind by name) to the interfaces of, the Work and Derivative Works thereof.

        "Contribution" shall mean any work of authorship, including the original version of the Work and any modifications or additions to that Work or Derivative Works thereof, that is intentionally submitted to Licensor for inclusion in the Work by the copyright owner or by an individual or Legal Entity authorized to submit on behalf of the copyright owner. For the purposes of this definition, "submitted" means any form of electronic, verbal, or written communication sent to the Licensor or its representatives, including but not limited to communication on electronic mailing lists, source code control systems, and issue tracking systems that are managed by, or on behalf of, the Licensor for the purpose of discussing and improving the Work, but excluding communication that is conspicuously marked or otherwise designated in writing by the copyright owner as "Not a Contribution."

        "Contributor" shall mean Licensor and any individual or Legal Entity on behalf of whom a Contribution has been received by Licensor and subsequently incorporated within the Work.
    2. Grant of Copyright License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce, prepare Derivative Works of, publicly display, publicly perform, sublicense, and distribute the Work and such Derivative Works in Source or Object form.
    3. Grant of Patent License. Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable (except as stated in this section) patent license to make, have made, use, offer to sell, sell, import, and otherwise transfer the Work, where such license applies only to those patent claims licensable by such Contributor that are necessarily infringed by their Contribution(s) alone or by combination of their Contribution(s) with the Work to which such Contribution(s) was submitted. If You institute patent litigation against any entity (including a cross-claim or counterclaim in a lawsuit) alleging that the Work or a Contribution incorporated within the Work constitutes direct or contributory patent infringement, then any patent licenses granted to You under this License for that Work shall terminate as of the date such litigation is filed.
    4. Redistribution. You may reproduce and distribute copies of the Work or Derivative Works thereof in any medium, with or without modifications, and in Source or Object form, provided that You meet the following conditions:
        (a) You must give any other recipients of the Work or Derivative Works a copy of this License; and
        (b) You must cause any modified files to carry prominent notices stating that You changed the files; and
        (c) You must retain, in the Source form of any Derivative Works that You distribute, all copyright, patent, trademark, and attribution notices from the Source form of the Work, excluding those notices that do not pertain to any part of the Derivative Works; and
        (d) If the Work includes a "NOTICE" text file as part of its distribution, then any Derivative Works that You distribute must include a readable copy of the attribution notices contained within such NOTICE file, excluding those notices that do not pertain to any part of the Derivative Works, in at least one of the following places: within a NOTICE text file distributed as part of the Derivative Works; within the Source form or documentation, if provided along with the Derivative Works; or, within a display generated by the Derivative Works, if and wherever such third-party notices normally appear. The contents of the NOTICE file are for informational purposes only and do not modify the License. You may add Your own attribution notices within Derivative Works that You distribute, alongside or as an addendum to the NOTICE text from the Work, provided that such additional attribution notices cannot be construed as modifying the License.

    You may add Your own copyright statement to Your modifications and may provide additional or different license terms and conditions for use, reproduction, or distribution of Your modifications, or for any such Derivative Works as a whole, provided Your use, reproduction, and distribution of the Work otherwise complies with the conditions stated in this License.
    5. Submission of Contributions. Unless You explicitly state otherwise, any Contribution intentionally submitted for inclusion in the Work by You to the Licensor shall be under the terms and conditions of this License, without any additional terms or conditions. Notwithstanding the above, nothing herein shall supersede or modify the terms of any separate license agreement you may have executed with Licensor regarding such Contributions.
    6. Trademarks. This License does not grant permission to use the trade names, trademarks, service marks, or product names of the Licensor, except as required for reasonable and customary use in describing the origin of the Work and reproducing the content of the NOTICE file.
    7. Disclaimer of Warranty. Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE. You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with Your exercise of permissions under this License.
    8. Limitation of Liability. In no event and under no legal theory, whether in tort (including negligence), contract, or otherwise, unless required by applicable law (such as deliberate and grossly negligent acts) or agreed to in writing, shall any Contributor be liable to You for damages, including any direct, indirect, special, incidental, or consequential damages of any character arising as a result of this License or out of the use or inability to use the Work (including but not limited to damages for loss of goodwill, work stoppage, computer failure or malfunction, or any and all other commercial damages or losses), even if such Contributor has been advised of the possibility of such damages.
    9. Accepting Warranty or Additional Liability. While redistributing the Work or Derivative Works thereof, You may choose to offer, and charge a fee for, acceptance of support, warranty, indemnity, or other liability obligations and/or rights consistent with this License. However, in accepting such obligations, You may act only on Your own behalf and on Your sole responsibility, not on behalf of any other Contributor, and only if You agree to indemnify, defend, and hold each Contributor harmless for any liability incurred by, or claims asserted against, such Contributor by reason of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

To apply the Apache License to your work, attach the following boilerplate notice, with the fields enclosed by brackets "[]" replaced with your own identifying information. (Don't include the brackets!) The text should be enclosed in the appropriate comment syntax for the file format. We also recommend that a file or class name and description of purpose be included on the same "printed page" as the copyright notice for easier identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

ISC License
-----------
Permission to use, copy, modify, and/or distribute this software for
any purpose with or without fee is hereby granted, provided that the
above copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.

MIT License
-----------
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

BSD 3-Clause License
--------------------
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived
   from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

MIT No Attribution (MIT-0)
--------------------------
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 

<!-- /notice:977c541bd25ffe36975dde25c028c0cd15ddf3d08243983b58e8a6a3d9447523 -->

## Notice 9b79539028e216e813e152d45f5c1ed5fdd0554426ad50270fb03134e7082dac

<!-- notice:9b79539028e216e813e152d45f5c1ed5fdd0554426ad50270fb03134e7082dac -->
Copyright (c) 2011, Google Inc. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in
    the documentation and/or other materials provided with the
    distribution.

  * Neither the name of Google nor the names of its contributors may
    be used to endorse or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

<!-- /notice:9b79539028e216e813e152d45f5c1ed5fdd0554426ad50270fb03134e7082dac -->

## Notice 9bbc1b3dc4674a9ebb12c2a62f54fe3c08672539717f8d05828f684b6cc419a3

<!-- notice:9bbc1b3dc4674a9ebb12c2a62f54fe3c08672539717f8d05828f684b6cc419a3 -->
The MIT License (MIT)

Copyright (c) 2015 Markus Westerlind

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.


<!-- /notice:9bbc1b3dc4674a9ebb12c2a62f54fe3c08672539717f8d05828f684b6cc419a3 -->

## Notice 9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3

<!-- notice:9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3 -->
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2023 The Fuchsia Authors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


<!-- /notice:9d185ac6703c4b0453974c0d85e9eee43e6941009296bb1f5eb0b54e2329e9f3 -->

## Notice 9e0dfd2dd4173a530e238cb6adb37aa78c34c6bc7444e0e10c1ab5d8881f63ba

<!-- notice:9e0dfd2dd4173a530e238cb6adb37aa78c34c6bc7444e0e10c1ab5d8881f63ba -->
Copyright (c) 2017 Artyom Pavlov

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:9e0dfd2dd4173a530e238cb6adb37aa78c34c6bc7444e0e10c1ab5d8881f63ba -->

## Notice a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499

<!-- notice:a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499 -->
Creative Commons Legal Code

CC0 1.0 Universal

    CREATIVE COMMONS CORPORATION IS NOT A LAW FIRM AND DOES NOT PROVIDE
    LEGAL SERVICES. DISTRIBUTION OF THIS DOCUMENT DOES NOT CREATE AN
    ATTORNEY-CLIENT RELATIONSHIP. CREATIVE COMMONS PROVIDES THIS
    INFORMATION ON AN "AS-IS" BASIS. CREATIVE COMMONS MAKES NO WARRANTIES
    REGARDING THE USE OF THIS DOCUMENT OR THE INFORMATION OR WORKS
    PROVIDED HEREUNDER, AND DISCLAIMS LIABILITY FOR DAMAGES RESULTING FROM
    THE USE OF THIS DOCUMENT OR THE INFORMATION OR WORKS PROVIDED
    HEREUNDER.

Statement of Purpose

The laws of most jurisdictions throughout the world automatically confer
exclusive Copyright and Related Rights (defined below) upon the creator
and subsequent owner(s) (each and all, an "owner") of an original work of
authorship and/or a database (each, a "Work").

Certain owners wish to permanently relinquish those rights to a Work for
the purpose of contributing to a commons of creative, cultural and
scientific works ("Commons") that the public can reliably and without fear
of later claims of infringement build upon, modify, incorporate in other
works, reuse and redistribute as freely as possible in any form whatsoever
and for any purposes, including without limitation commercial purposes.
These owners may contribute to the Commons to promote the ideal of a free
culture and the further production of creative, cultural and scientific
works, or to gain reputation or greater distribution for their Work in
part through the use and efforts of others.

For these and/or other purposes and motivations, and without any
expectation of additional consideration or compensation, the person
associating CC0 with a Work (the "Affirmer"), to the extent that he or she
is an owner of Copyright and Related Rights in the Work, voluntarily
elects to apply CC0 to the Work and publicly distribute the Work under its
terms, with knowledge of his or her Copyright and Related Rights in the
Work and the meaning and intended legal effect of CC0 on those rights.

1. Copyright and Related Rights. A Work made available under CC0 may be
protected by copyright and related or neighboring rights ("Copyright and
Related Rights"). Copyright and Related Rights include, but are not
limited to, the following:

  i. the right to reproduce, adapt, distribute, perform, display,
     communicate, and translate a Work;
 ii. moral rights retained by the original author(s) and/or performer(s);
iii. publicity and privacy rights pertaining to a person's image or
     likeness depicted in a Work;
 iv. rights protecting against unfair competition in regards to a Work,
     subject to the limitations in paragraph 4(a), below;
  v. rights protecting the extraction, dissemination, use and reuse of data
     in a Work;
 vi. database rights (such as those arising under Directive 96/9/EC of the
     European Parliament and of the Council of 11 March 1996 on the legal
     protection of databases, and under any national implementation
     thereof, including any amended or successor version of such
     directive); and
vii. other similar, equivalent or corresponding rights throughout the
     world based on applicable law or treaty, and any national
     implementations thereof.

2. Waiver. To the greatest extent permitted by, but not in contravention
of, applicable law, Affirmer hereby overtly, fully, permanently,
irrevocably and unconditionally waives, abandons, and surrenders all of
Affirmer's Copyright and Related Rights and associated claims and causes
of action, whether now known or unknown (including existing as well as
future claims and causes of action), in the Work (i) in all territories
worldwide, (ii) for the maximum duration provided by applicable law or
treaty (including future time extensions), (iii) in any current or future
medium and for any number of copies, and (iv) for any purpose whatsoever,
including without limitation commercial, advertising or promotional
purposes (the "Waiver"). Affirmer makes the Waiver for the benefit of each
member of the public at large and to the detriment of Affirmer's heirs and
successors, fully intending that such Waiver shall not be subject to
revocation, rescission, cancellation, termination, or any other legal or
equitable action to disrupt the quiet enjoyment of the Work by the public
as contemplated by Affirmer's express Statement of Purpose.

3. Public License Fallback. Should any part of the Waiver for any reason
be judged legally invalid or ineffective under applicable law, then the
Waiver shall be preserved to the maximum extent permitted taking into
account Affirmer's express Statement of Purpose. In addition, to the
extent the Waiver is so judged Affirmer hereby grants to each affected
person a royalty-free, non transferable, non sublicensable, non exclusive,
irrevocable and unconditional license to exercise Affirmer's Copyright and
Related Rights in the Work (i) in all territories worldwide, (ii) for the
maximum duration provided by applicable law or treaty (including future
time extensions), (iii) in any current or future medium and for any number
of copies, and (iv) for any purpose whatsoever, including without
limitation commercial, advertising or promotional purposes (the
"License"). The License shall be deemed effective as of the date CC0 was
applied by Affirmer to the Work. Should any part of the License for any
reason be judged legally invalid or ineffective under applicable law, such
partial invalidity or ineffectiveness shall not invalidate the remainder
of the License, and in such case Affirmer hereby affirms that he or she
will not (i) exercise any of his or her remaining Copyright and Related
Rights in the Work or (ii) assert any associated claims and causes of
action with respect to the Work, in either case contrary to Affirmer's
express Statement of Purpose.

4. Limitations and Disclaimers.

 a. No trademark or patent rights held by Affirmer are waived, abandoned,
    surrendered, licensed or otherwise affected by this document.
 b. Affirmer offers the Work as-is and makes no representations or
    warranties of any kind concerning the Work, express, implied,
    statutory or otherwise, including without limitation warranties of
    title, merchantability, fitness for a particular purpose, non
    infringement, or the absence of latent or other defects, accuracy, or
    the present or absence of errors, whether or not discoverable, all to
    the greatest extent permissible under applicable law.
 c. Affirmer disclaims responsibility for clearing rights of other persons
    that may apply to the Work or any use thereof, including without
    limitation any person's Copyright and Related Rights in the Work.
    Further, Affirmer disclaims responsibility for obtaining any necessary
    consents, permissions or other rights required for any use of the
    Work.
 d. Affirmer understands and acknowledges that Creative Commons is not a
    party to this document and has no duty or obligation with respect to
    this CC0 or use of the Work.

<!-- /notice:a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499 -->

## Notice a46200592eb193853527250da098e6bb0c75424e7a2c7db8da526c4f301c3d88

<!-- notice:a46200592eb193853527250da098e6bb0c75424e7a2c7db8da526c4f301c3d88 -->
Copyright (c) 2013  Julien Pommier ( pommier@modartt.com )

Based on original fortran 77 code from FFTPACKv4 from NETLIB,
authored by Dr Paul Swarztrauber of NCAR, in 1985.

As confirmed by the NCAR fftpack software curators, the following
FFTPACKv5 license applies to FFTPACKv4 sources. My changes are
released under the same terms.

FFTPACK license:

http://www.cisl.ucar.edu/css/software/fftpack5/ftpk.html

Copyright (c) 2004 the University Corporation for Atmospheric
Research ("UCAR"). All rights reserved. Developed by NCAR's
Computational and Information Systems Laboratory, UCAR,
www.cisl.ucar.edu.

Redistribution and use of the Software in source and binary forms,
with or without modification, is permitted provided that the
following conditions are met:

- Neither the names of NCAR's Computational and Information Systems
Laboratory, the University Corporation for Atmospheric Research,
nor the names of its sponsors or contributors may be used to
endorse or promote products derived from this Software without
specific prior written permission.

- Redistributions of source code must retain the above copyright
notices, this list of conditions, and the disclaimer below.

- Redistributions in binary form must reproduce the above copyright
notice, this list of conditions, and the disclaimer below in the
documentation and/or other materials provided with the
distribution.

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING, BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE CONTRIBUTORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS WITH THE
SOFTWARE.

<!-- /notice:a46200592eb193853527250da098e6bb0c75424e7a2c7db8da526c4f301c3d88 -->

## Notice a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513

<!-- notice:a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513 -->
Copyright (c) 2017 Pierre Chifflier

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:a5c61b93b6ee1d104af9920cf020ff3c7efe818e31fe562c72261847a728f513 -->

## Notice a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2

<!-- notice:a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2 -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:a60eea817514531668d7e00765731449fe14d059d3249e0bc93b36de45f759f2 -->

## Notice a825bd853ab71619a4923d7b4311221427848070ff44d990da39b0b274c1683f

<!-- notice:a825bd853ab71619a4923d7b4311221427848070ff44d990da39b0b274c1683f -->
The MIT License (MIT)

Copyright (c) 2014 Paho Lurie-Gregg

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:a825bd853ab71619a4923d7b4311221427848070ff44d990da39b0b274c1683f -->

## Notice a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5

<!-- notice:a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5 -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:a9040321c3712d8fd0b09cf52b17445de04a23a10165049ae187cd39e5c86be5 -->

## Notice aa72991ac35b4de0034da0afe943e62b48c4092fc2ba13ae47806d8e9a4ad551

<!-- notice:aa72991ac35b4de0034da0afe943e62b48c4092fc2ba13ae47806d8e9a4ad551 -->
Copyright (c) 2015 steffengy

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<!-- /notice:aa72991ac35b4de0034da0afe943e62b48c4092fc2ba13ae47806d8e9a4ad551 -->

## Notice aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf

<!-- notice:aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf -->
                              Apache License
                        Version 2.0, January 2004
                     https://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

	https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:aaff376532ea30a0cd5330b9502ad4a4c8bf769c539c87ffe78819d188a18ebf -->

## Notice ab00a482b6a3902e40211b43c5d0441962ea99b6cc7c25c0f243fa270b78d482

<!-- notice:ab00a482b6a3902e40211b43c5d0441962ea99b6cc7c25c0f243fa270b78d482 -->
Copyright (c) 2011, The WebRTC project authors. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in
    the documentation and/or other materials provided with the
    distribution.

  * Neither the name of Google nor the names of its contributors may
    be used to endorse or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

<!-- /notice:ab00a482b6a3902e40211b43c5d0441962ea99b6cc7c25c0f243fa270b78d482 -->

## Notice ad64fcb9589f162720f3cc5010ad76ca6ad3764e11861f9192c489df176bb71d

<!-- notice:ad64fcb9589f162720f3cc5010ad76ca6ad3764e11861f9192c489df176bb71d -->
Copyright (c) 2020-2023 The RustCrypto Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:ad64fcb9589f162720f3cc5010ad76ca6ad3764e11861f9192c489df176bb71d -->

## Notice ae9baa7beea910273c2f384c2a6b721fb7bd02bda3436074a1072e4ee689f985

<!-- notice:ae9baa7beea910273c2f384c2a6b721fb7bd02bda3436074a1072e4ee689f985 -->
Copyright (c) 2020-2025 The RustCrypto Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:ae9baa7beea910273c2f384c2a6b721fb7bd02bda3436074a1072e4ee689f985 -->

## Notice afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6

<!-- notice:afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6 -->
Copyright (c) 2023-present PyO3 Project and Contributors.  https://github.com/PyO3

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:afcbe3b2e6b37172b5a9ca869ee4c0b8cdc09316e5d4384864154482c33e5af6 -->

## Notice b1cf9a3333ca78152b859012cd4a804156e5243e9ca20ad1df7327ba5ea7405c

<!-- notice:b1cf9a3333ca78152b859012cd4a804156e5243e9ca20ad1df7327ba5ea7405c -->
                              Apache License
                        Version 2.0, January 2004
                     http://www.apache.org/licenses/

TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

1. Definitions.

   "License" shall mean the terms and conditions for use, reproduction,
   and distribution as defined by Sections 1 through 9 of this document.

   "Licensor" shall mean the copyright owner or entity authorized by
   the copyright owner that is granting the License.

   "Legal Entity" shall mean the union of the acting entity and all
   other entities that control, are controlled by, or are under common
   control with that entity. For the purposes of this definition,
   "control" means (i) the power, direct or indirect, to cause the
   direction or management of such entity, whether by contract or
   otherwise, or (ii) ownership of fifty percent (50%) or more of the
   outstanding shares, or (iii) beneficial ownership of such entity.

   "You" (or "Your") shall mean an individual or Legal Entity
   exercising permissions granted by this License.

   "Source" form shall mean the preferred form for making modifications,
   including but not limited to software source code, documentation
   source, and configuration files.

   "Object" form shall mean any form resulting from mechanical
   transformation or translation of a Source form, including but
   not limited to compiled object code, generated documentation,
   and conversions to other media types.

   "Work" shall mean the work of authorship, whether in Source or
   Object form, made available under the License, as indicated by a
   copyright notice that is included in or attached to the work
   (an example is provided in the Appendix below).

   "Derivative Works" shall mean any work, whether in Source or Object
   form, that is based on (or derived from) the Work and for which the
   editorial revisions, annotations, elaborations, or other modifications
   represent, as a whole, an original work of authorship. For the purposes
   of this License, Derivative Works shall not include works that remain
   separable from, or merely link (or bind by name) to the interfaces of,
   the Work and Derivative Works thereof.

   "Contribution" shall mean any work of authorship, including
   the original version of the Work and any modifications or additions
   to that Work or Derivative Works thereof, that is intentionally
   submitted to Licensor for inclusion in the Work by the copyright owner
   or by an individual or Legal Entity authorized to submit on behalf of
   the copyright owner. For the purposes of this definition, "submitted"
   means any form of electronic, verbal, or written communication sent
   to the Licensor or its representatives, including but not limited to
   communication on electronic mailing lists, source code control systems,
   and issue tracking systems that are managed by, or on behalf of, the
   Licensor for the purpose of discussing and improving the Work, but
   excluding communication that is conspicuously marked or otherwise
   designated in writing by the copyright owner as "Not a Contribution."

   "Contributor" shall mean Licensor and any individual or Legal Entity
   on behalf of whom a Contribution has been received by Licensor and
   subsequently incorporated within the Work.

2. Grant of Copyright License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   copyright license to reproduce, prepare Derivative Works of,
   publicly display, publicly perform, sublicense, and distribute the
   Work and such Derivative Works in Source or Object form.

3. Grant of Patent License. Subject to the terms and conditions of
   this License, each Contributor hereby grants to You a perpetual,
   worldwide, non-exclusive, no-charge, royalty-free, irrevocable
   (except as stated in this section) patent license to make, have made,
   use, offer to sell, sell, import, and otherwise transfer the Work,
   where such license applies only to those patent claims licensable
   by such Contributor that are necessarily infringed by their
   Contribution(s) alone or by combination of their Contribution(s)
   with the Work to which such Contribution(s) was submitted. If You
   institute patent litigation against any entity (including a
   cross-claim or counterclaim in a lawsuit) alleging that the Work
   or a Contribution incorporated within the Work constitutes direct
   or contributory patent infringement, then any patent licenses
   granted to You under this License for that Work shall terminate
   as of the date such litigation is filed.

4. Redistribution. You may reproduce and distribute copies of the
   Work or Derivative Works thereof in any medium, with or without
   modifications, and in Source or Object form, provided that You
   meet the following conditions:

   (a) You must give any other recipients of the Work or
       Derivative Works a copy of this License; and

   (b) You must cause any modified files to carry prominent notices
       stating that You changed the files; and

   (c) You must retain, in the Source form of any Derivative Works
       that You distribute, all copyright, patent, trademark, and
       attribution notices from the Source form of the Work,
       excluding those notices that do not pertain to any part of
       the Derivative Works; and

   (d) If the Work includes a "NOTICE" text file as part of its
       distribution, then any Derivative Works that You distribute must
       include a readable copy of the attribution notices contained
       within such NOTICE file, excluding those notices that do not
       pertain to any part of the Derivative Works, in at least one
       of the following places: within a NOTICE text file distributed
       as part of the Derivative Works; within the Source form or
       documentation, if provided along with the Derivative Works; or,
       within a display generated by the Derivative Works, if and
       wherever such third-party notices normally appear. The contents
       of the NOTICE file are for informational purposes only and
       do not modify the License. You may add Your own attribution
       notices within Derivative Works that You distribute, alongside
       or as an addendum to the NOTICE text from the Work, provided
       that such additional attribution notices cannot be construed
       as modifying the License.

   You may add Your own copyright statement to Your modifications and
   may provide additional or different license terms and conditions
   for use, reproduction, or distribution of Your modifications, or
   for any such Derivative Works as a whole, provided Your use,
   reproduction, and distribution of the Work otherwise complies with
   the conditions stated in this License.

5. Submission of Contributions. Unless You explicitly state otherwise,
   any Contribution intentionally submitted for inclusion in the Work
   by You to the Licensor shall be under the terms and conditions of
   this License, without any additional terms or conditions.
   Notwithstanding the above, nothing herein shall supersede or modify
   the terms of any separate license agreement you may have executed
   with Licensor regarding such Contributions.

6. Trademarks. This License does not grant permission to use the trade
   names, trademarks, service marks, or product names of the Licensor,
   except as required for reasonable and customary use in describing the
   origin of the Work and reproducing the content of the NOTICE file.

7. Disclaimer of Warranty. Unless required by applicable law or
   agreed to in writing, Licensor provides the Work (and each
   Contributor provides its Contributions) on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
   implied, including, without limitation, any warranties or conditions
   of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
   PARTICULAR PURPOSE. You are solely responsible for determining the
   appropriateness of using or redistributing the Work and assume any
   risks associated with Your exercise of permissions under this License.

8. Limitation of Liability. In no event and under no legal theory,
   whether in tort (including negligence), contract, or otherwise,
   unless required by applicable law (such as deliberate and grossly
   negligent acts) or agreed to in writing, shall any Contributor be
   liable to You for damages, including any direct, indirect, special,
   incidental, or consequential damages of any character arising as a
   result of this License or out of the use or inability to use the
   Work (including but not limited to damages for loss of goodwill,
   work stoppage, computer failure or malfunction, or any and all
   other commercial damages or losses), even if such Contributor
   has been advised of the possibility of such damages.

9. Accepting Warranty or Additional Liability. While redistributing
   the Work or Derivative Works thereof, You may choose to offer,
   and charge a fee for, acceptance of support, warranty, indemnity,
   or other liability obligations and/or rights consistent with this
   License. However, in accepting such obligations, You may act only
   on Your own behalf and on Your sole responsibility, not on behalf
   of any other Contributor, and only if You agree to indemnify,
   defend, and hold each Contributor harmless for any liability
   incurred by, or claims asserted against, such Contributor by reason
   of your accepting any such warranty or additional liability.

END OF TERMS AND CONDITIONS

APPENDIX: How to apply the Apache License to your work.

   To apply the Apache License to your work, attach the following
   boilerplate notice, with the fields enclosed by brackets "[]"
   replaced with your own identifying information. (Don't include
   the brackets!)  The text should be enclosed in the appropriate
   comment syntax for the file format. We also recommend that a
   file or class name and description of purpose be included on the
   same "printed page" as the copyright notice for easier
   identification within third-party archives.

Copyright [yyyy] [name of copyright owner]

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


<!-- /notice:b1cf9a3333ca78152b859012cd4a804156e5243e9ca20ad1df7327ba5ea7405c -->

## Notice b1d6df41ed3aa96806e74c729444d7c121d90e6660a6aed01d298e03fde475a0

<!-- notice:b1d6df41ed3aa96806e74c729444d7c121d90e6660a6aed01d298e03fde475a0 -->
The MIT License (MIT)

Copyright (c) 2016 RustAudio Developers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:b1d6df41ed3aa96806e74c729444d7c121d90e6660a6aed01d298e03fde475a0 -->

## Notice b29f8b01452350c20dd1af16ef83b598fea3053578ccc1c7a0ef40e57be2620f

<!-- notice:b29f8b01452350c20dd1af16ef83b598fea3053578ccc1c7a0ef40e57be2620f -->
Copyright © 2015, Simonas Kazlauskas

Permission to use, copy, modify, and/or distribute this software for any purpose with or without
fee is hereby granted, provided that the above copyright notice and this permission notice appear
in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF
THIS SOFTWARE.

<!-- /notice:b29f8b01452350c20dd1af16ef83b598fea3053578ccc1c7a0ef40e57be2620f -->

## Notice b3470648aff02beb36d7a53240fc9260ed80ed93bd43bace6b67d7ef7336ee33

<!-- notice:b3470648aff02beb36d7a53240fc9260ed80ed93bd43bace6b67d7ef7336ee33 -->
Copyright (c) 2018-2023 RustCrypto Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:b3470648aff02beb36d7a53240fc9260ed80ed93bd43bace6b67d7ef7336ee33 -->

## Notice b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5

<!-- notice:b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5 -->
Copyright (c) 2013-2025 The rust-url developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:b38f11f6096706e6de553dabe2a7ed142d59b6fa8c97e290c67496154745cdd5 -->

## Notice b4eb00df6e2a4d22518fcaa6a2b4646f249b3a3c9814509b22bd2091f1392ff1

<!-- notice:b4eb00df6e2a4d22518fcaa6a2b4646f249b3a3c9814509b22bd2091f1392ff1 -->
Copyright (c) 2006-2009 Graydon Hoare
Copyright (c) 2009-2013 Mozilla Foundation
Copyright (c) 2016 Artyom Pavlov

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:b4eb00df6e2a4d22518fcaa6a2b4646f249b3a3c9814509b22bd2091f1392ff1 -->

## Notice b50b376e7d24a0598488b730c3034ffcd0b58dd36c0913a24b9903a3cfd04bf7

<!-- notice:b50b376e7d24a0598488b730c3034ffcd0b58dd36c0913a24b9903a3cfd04bf7 -->
SPDX-License-Identifier: ISC AND (Apache-2.0 OR ISC)


Apache 2.0 license
-------------------------------------


                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS


ISC license
-------------------------------------


Copyright Amazon.com, Inc. or its affiliates.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

<!-- /notice:b50b376e7d24a0598488b730c3034ffcd0b58dd36c0913a24b9903a3cfd04bf7 -->

## Notice b68ad1a3367b825447089e1f8d6829b97f47a89eb78d2f4ebaef4672f5606186

<!-- notice:b68ad1a3367b825447089e1f8d6829b97f47a89eb78d2f4ebaef4672f5606186 -->
The MIT License (MIT)

Copyright (c) 2015-2020 Julien Cretin
Copyright (c) 2017-2020 Google Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:b68ad1a3367b825447089e1f8d6829b97f47a89eb78d2f4ebaef4672f5606186 -->

## Notice b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e

<!-- notice:b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e -->
The MIT License (MIT)
Copyright (c) 2017-2018 Sergio Benitez

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software is furnished to do so,
subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<!-- /notice:b7e650f3fce5c53249d1cdc608b54df156a97edd636cf9d23498d0cfe7aec63e -->

## Notice bada9e7ed8dc00d63502053c455d7c8d7575dfb7e8277a2a832531844d900682

<!-- notice:bada9e7ed8dc00d63502053c455d7c8d7575dfb7e8277a2a832531844d900682 -->
Copyright (c) 2020-2022 The RustCrypto Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:bada9e7ed8dc00d63502053c455d7c8d7575dfb7e8277a2a832531844d900682 -->

## Notice be4be5d77424833edf31f53fc1f1cecb6996b9e2d747d9e6fb8f878362ebc92b

<!-- notice:be4be5d77424833edf31f53fc1f1cecb6996b9e2d747d9e6fb8f878362ebc92b -->
All PipeWire source files are licensed under the MIT License.
(see file COPYING for details)

With the exception of:

  libspa-alsa.so in spa/plugins/alsa, which contains LGPL code from
                  Pulseaudio and is thus licensed as LGPL.

  libjackserver.so which links against the GPL2 jack/control.h, which
                  makes it GPL2


<!-- /notice:be4be5d77424833edf31f53fc1f1cecb6996b9e2d747d9e6fb8f878362ebc92b -->

## Notice c09aae9d3c77b531f56351a9947bc7446511d6b025b3255312d3e3442a9a7583

<!-- notice:c09aae9d3c77b531f56351a9947bc7446511d6b025b3255312d3e3442a9a7583 -->
The MIT License (MIT)

Copyright (c) 2015 Bartłomiej Kamiński

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
<!-- /notice:c09aae9d3c77b531f56351a9947bc7446511d6b025b3255312d3e3442a9a7583 -->

## Notice c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b

<!-- notice:c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b -->
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright (c) Microsoft Corporation.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

<!-- /notice:c16f8dcf1a368b83be78d826ea23de4079fe1b4469a0ab9ee20563f37ff3d44b -->

## Notice c23953d9deb0a3312dbeaf6c128a657f3591acee45067612fa68405eaa4525db

<!-- notice:c23953d9deb0a3312dbeaf6c128a657f3591acee45067612fa68405eaa4525db -->
BSD 3-Clause License

Copyright (c) 2013, Jyun-Yan You
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

<!-- /notice:c23953d9deb0a3312dbeaf6c128a657f3591acee45067612fa68405eaa4525db -->

## Notice c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383

<!-- notice:c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383 -->
    MIT License

    Copyright (c) Microsoft Corporation.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE

<!-- /notice:c2cfccb812fe482101a8f04597dfc5a9991a6b2748266c47ac91b6a5aae15383 -->

## Notice c30152c94a6d75e021adbc52b3a52470366a46edb917e17deae3259251af244c

<!-- notice:c30152c94a6d75e021adbc52b3a52470366a46edb917e17deae3259251af244c -->
Copyright Mozilla Foundation

Licensed under the Apache License (Version 2.0), or the MIT license,
(the "Licenses") at your option. You may not use this file except in
compliance with one of the Licenses. You may obtain copies of the
Licenses at:

   https://www.apache.org/licenses/LICENSE-2.0
   https://opensource.org/licenses/MIT

Unless required by applicable law or agreed to in writing, software
distributed under the Licenses is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licenses for the specific language governing permissions and
limitations under the Licenses.

--

Test code is dedicated to the Public Domain when so designated (see
the individual files for PD/CC0-dedicated sections).

--

The implementation for Utf8CharIndices was adapted from the
CharIndices implementation of the Rust standard library at revision
ab32548539ec38a939c1b58599249f3b54130026
(https://github.com/rust-lang/rust/blob/ab32548539ec38a939c1b58599249f3b54130026/library/core/src/str/iter.rs).

Excerpt from https://github.com/rust-lang/rust/blob/ab32548539ec38a939c1b58599249f3b54130026/COPYRIGHT ,
which refers to
https://github.com/rust-lang/rust/blob/ab32548539ec38a939c1b58599249f3b54130026/LICENSE-APACHE
and
https://github.com/rust-lang/rust/blob/ab32548539ec38a939c1b58599249f3b54130026/LICENSE-MIT
:

For full authorship information, see the version control history or
https://thanks.rust-lang.org

Except as otherwise noted (below and/or in individual files), Rust is
licensed under the Apache License, Version 2.0 <LICENSE-APACHE> or
<http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
<LICENSE-MIT> or <http://opensource.org/licenses/MIT>, at your option.

<!-- /notice:c30152c94a6d75e021adbc52b3a52470366a46edb917e17deae3259251af244c -->

## Notice c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08

<!-- notice:c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08 -->
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "{}"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright {yyyy} {name of copyright owner}

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


<!-- /notice:c6596eb7be8581c18be736c846fb9173b69eccf6ef94c5135893ec56bd92ba08 -->

## Notice c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4

<!-- notice:c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4 -->
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

<!-- /notice:c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4 -->

## Notice c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6

<!-- notice:c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6 -->
Copyright The pipewire-rs Contributors.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice (including the next
paragraph) shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:c786d27ff72139f9c5dc2ff460c88fd59a6aed40be33c4d5e50bfaa2c1f43df6 -->

## Notice c79a7fea0e3cac04cd43f20e7b648e5a0ff8fa5344e644b0ee09ca1162b62747

<!-- notice:c79a7fea0e3cac04cd43f20e7b648e5a0ff8fa5344e644b0ee09ca1162b62747 -->

                                 Apache License
                           Version 2.0, January 2004
                        https://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       https://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


<!-- /notice:c79a7fea0e3cac04cd43f20e7b648e5a0ff8fa5344e644b0ee09ca1162b62747 -->

## Notice c995204cc6bad2ed67dd41f7d89bb9f1a9d48e0edd745732b30640d7912089a4

<!-- notice:c995204cc6bad2ed67dd41f7d89bb9f1a9d48e0edd745732b30640d7912089a4 -->
Copyright (c) 2021-2023 The RustCrypto Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:c995204cc6bad2ed67dd41f7d89bb9f1a9d48e0edd745732b30640d7912089a4 -->

## Notice c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5

<!-- notice:c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5 -->
Copyright (c) 2016 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:c9a75f18b9ab2927829a208fc6aa2cf4e63b8420887ba29cdb265d6619ae82d5 -->

## Notice cb3c929a05e6cbc9de9ab06a4c57eeb60ca8c724bef6c138c87d3a577e27aa14

<!-- notice:cb3c929a05e6cbc9de9ab06a4c57eeb60ca8c724bef6c138c87d3a577e27aa14 -->
The MIT License (MIT)

Copyright (c) 2017 Andrew Gallant

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

<!-- /notice:cb3c929a05e6cbc9de9ab06a4c57eeb60ca8c724bef6c138c87d3a577e27aa14 -->

## Notice cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d

<!-- notice:cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d -->
Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<!-- /notice:cb5aedb296c5246d1f22e9099f925a65146f9f0d6b4eebba97fd27a6cdbbab2d -->

## Notice cedfcc7ace1639adb054bd4a19b6f8585ccb2429a60b4bf51bfeb0601058c22c

<!-- notice:cedfcc7ace1639adb054bd4a19b6f8585ccb2429a60b4bf51bfeb0601058c22c -->
Copyright (c) 2017 Tim Visée

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


<!-- /notice:cedfcc7ace1639adb054bd4a19b6f8585ccb2429a60b4bf51bfeb0601058c22c -->

## Notice cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30

<!-- notice:cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 -->

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

<!-- /notice:cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30 -->

## Notice d027e91dbc9cdbb2f1190068e498bd6b61cff022b6a032b191021ba658d96111

<!-- notice:d027e91dbc9cdbb2f1190068e498bd6b61cff022b6a032b191021ba658d96111 -->
LICENSE:
        This project is triple-licensed under the MIT License, the Apache
        License, Version 2.0, and the GNU Lesser General Public License,
        Version 2.1+.

AUTHORS-MIT:
        Permission is hereby granted, free of charge, to any person obtaining a
        copy of this software and associated documentation files (the
        "Software"), to deal in the Software without restriction, including
        without limitation the rights to use, copy, modify, merge, publish,
        distribute, sublicense, and/or sell copies of the Software, and to
        permit persons to whom the Software is furnished to do so, subject to
        the following conditions:

        The above copyright notice and this permission notice shall be included
        in all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
        OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
        MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
        IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
        CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
        TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
        SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

AUTHORS-ASL:
        Licensed under the Apache License, Version 2.0 (the "License");
        you may not use this file except in compliance with the License.
        You may obtain a copy of the License at

                http://www.apache.org/licenses/LICENSE-2.0

        Unless required by applicable law or agreed to in writing, software
        distributed under the License is distributed on an "AS IS" BASIS,
        WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
        See the License for the specific language governing permissions and
        limitations under the License.

AUTHORS-LGPL:
        This program is free software; you can redistribute it and/or modify it
        under the terms of the GNU Lesser General Public License as published
        by the Free Software Foundation; either version 2.1 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful, but
        WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
        Lesser General Public License for more details.

        You should have received a copy of the GNU Lesser General Public License
        along with this program; If not, see <http://www.gnu.org/licenses/>.

COPYRIGHT: (ordered alphabetically)
        Copyright (C) 2017-2023 Red Hat, Inc.
        Copyright (C) 2019-2023 Microsoft Corporation
        Copyright (C) 2022-2023 David Rheinsberg

AUTHORS: (ordered alphabetically)
        Alan Egerton <eggyal@gmail.com>
        Alex James <theracermaster@gmail.com>
        Ayush Singh <ayushsingh1325@gmail.com>
        Boris-Chengbiao Zhou <bobo1239@web.de>
        Bret Barkelew <bret@corthon.com>
        Christopher Zurcher <christopher.zurcher@microsoft.com>
        David Rheinsberg <david@readahead.eu>
        Dmitry Mostovenko <trueberserker@gmail.com>
        Hiroki Tokunaga <tokusan441@gmail.com>
        Joe Richey <joerichey@google.com>
        John Schock <joschock@microsoft.com>
        Michael Kubacki <michael.kubacki@microsoft.com>
        Oliver Smith-Denny <osde@microsoft.com>
        Richard Wiedenhöft <richard@wiedenhoeft.xyz>
        Rob Bradford <robert.bradford@intel.com>, <rbradford@rivosinc.com>
        Tom Gundersen <teg@jklm.no>
        Trevor Gross <tmgross@umich.edu>

<!-- /notice:d027e91dbc9cdbb2f1190068e498bd6b61cff022b6a032b191021ba658d96111 -->

## Notice d09216dc1ea5f273997667935a8d6514d80f00b89fb6954ecc3a43e0a6e360de

<!-- notice:d09216dc1ea5f273997667935a8d6514d80f00b89fb6954ecc3a43e0a6e360de -->
Copyright (c) 2017-2023 Geoffroy Couprie

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

<!-- /notice:d09216dc1ea5f273997667935a8d6514d80f00b89fb6954ecc3a43e0a6e360de -->

## Notice d1fc1bc0d155df60b2e7705b6b2ae02a05c96f948e1cec6e2fb86360b09f346b

<!-- notice:d1fc1bc0d155df60b2e7705b6b2ae02a05c96f948e1cec6e2fb86360b09f346b -->
Copyright (c) 2016-2017 Isis Agora Lovecruft, Henry de Valence. All rights reserved.
Copyright (c) 2016-2024 Isis Agora Lovecruft. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 

<!-- /notice:d1fc1bc0d155df60b2e7705b6b2ae02a05c96f948e1cec6e2fb86360b09f346b -->

## Notice d3cdb764b98283ee7c3a3cea8d374e2a2957322374378d1f3263f4d512741fc3

<!-- notice:d3cdb764b98283ee7c3a3cea8d374e2a2957322374378d1f3263f4d512741fc3 -->
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2019 Akhil Velagapudi

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

<!-- /notice:d3cdb764b98283ee7c3a3cea8d374e2a2957322374378d1f3263f4d512741fc3 -->

## Notice d5c22aa3118d240e877ad41c5d9fa232f9c77d757d4aac0c2f943afc0a95e0ef

<!-- notice:d5c22aa3118d240e877ad41c5d9fa232f9c77d757d4aac0c2f943afc0a95e0ef -->
Copyright (c) 2018-2019 The RustCrypto Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:d5c22aa3118d240e877ad41c5d9fa232f9c77d757d4aac0c2f943afc0a95e0ef -->

## Notice d9771b8c6cf4426d3846de54c1febe20907f1eeadf7adfb5ade89a83bd9ea77f

<!-- notice:d9771b8c6cf4426d3846de54c1febe20907f1eeadf7adfb5ade89a83bd9ea77f -->
(C) Copyright 2016 Jethro G. Beekman

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:d9771b8c6cf4426d3846de54c1febe20907f1eeadf7adfb5ade89a83bd9ea77f -->

## Notice db11fec9946737df39ca3898d9cd8c10ec6f6c3a884a6802b0ad0b81b4e8f23a

<!-- notice:db11fec9946737df39ca3898d9cd8c10ec6f6c3a884a6802b0ad0b81b4e8f23a -->
MIT OR Apache-2.0
<!-- /notice:db11fec9946737df39ca3898d9cd8c10ec6f6c3a884a6802b0ad0b81b4e8f23a -->

## Notice dbe1fff0fb1314b6af94f161511406275cf01c5a32441fbf24528a57a051d599

<!-- notice:dbe1fff0fb1314b6af94f161511406275cf01c5a32441fbf24528a57a051d599 -->
Minimal-lexical is dual licensed under the Apache 2.0 license as well as the MIT
license. See the LICENCE-MIT and the LICENCE-APACHE files for the licenses.

---

`src/bellerophon.rs` is loosely based off the Golang implementation,
found [here](https://github.com/golang/go/blob/b10849fbb97a2244c086991b4623ae9f32c212d0/src/strconv/extfloat.go).
That code (used if the `compact` feature is enabled) is subject to a
[3-clause BSD license](https://github.com/golang/go/blob/b10849fbb97a2244c086991b4623ae9f32c212d0/LICENSE):

Copyright (c) 2009 The Go Authors. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

   * Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above
copyright notice, this list of conditions and the following disclaimer
in the documentation and/or other materials provided with the
distribution.
   * Neither the name of Google Inc. nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

<!-- /notice:dbe1fff0fb1314b6af94f161511406275cf01c5a32441fbf24528a57a051d599 -->

## Notice dc91f8200e4b2a1f9261035d4c18c33c246911a6c0f7b543d75347e61b249cff

<!-- notice:dc91f8200e4b2a1f9261035d4c18c33c246911a6c0f7b543d75347e61b249cff -->
Copyright (c) 2017 http-rs authors

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:dc91f8200e4b2a1f9261035d4c18c33c246911a6c0f7b543d75347e61b249cff -->

## Notice debe6fed7ac143217c7f533759c54b14f18cd01d5fe195c51d83c2ae2d136cb4

<!-- notice:debe6fed7ac143217c7f533759c54b14f18cd01d5fe195c51d83c2ae2d136cb4 -->
Copyright (c) 2019-2026 est31 <MTest31@outlook.com> and contributors

Licensed under MIT or Apache License 2.0,
at your option.

The full list of contributors can be obtained by looking
at the VCS log (originally, this crate was git versioned,
there you can do "git shortlog -sn" for this task).

MIT License
-----------

The MIT License (MIT)

Copyright (c) 2019-2026 est31 <MTest31@outlook.com> and contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.



Apache License, version 2.0
---------------------------
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

<!-- /notice:debe6fed7ac143217c7f533759c54b14f18cd01d5fe195c51d83c2ae2d136cb4 -->

## Notice e2e245f2b566d0bfafb0f6a04c16b82d710c4e6e7d799e39bb4ef6e541b85b98

<!-- notice:e2e245f2b566d0bfafb0f6a04c16b82d710c4e6e7d799e39bb4ef6e541b85b98 -->
Copyright (c) Jacob Pratt

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:e2e245f2b566d0bfafb0f6a04c16b82d710c4e6e7d799e39bb4ef6e541b85b98 -->

## Notice e2f59ff41d9d03adc3dcf3deff170f8c8cf4a6eb4a9b174762a7656d23200ffa

<!-- notice:e2f59ff41d9d03adc3dcf3deff170f8c8cf4a6eb4a9b174762a7656d23200ffa -->
Copyright (c) 2017, Mozilla
Copyright (c) 2007-2017, Jean-Marc Valin
Copyright (c) 2005-2017, Xiph.Org Foundation
Copyright (c) 2003-2004, Mark Borgerding

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

- Redistributions of source code must retain the above copyright
notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.

- Neither the name of the Xiph.Org Foundation nor the names of its
contributors may be used to endorse or promote products derived from
this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE FOUNDATION
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

<!-- /notice:e2f59ff41d9d03adc3dcf3deff170f8c8cf4a6eb4a9b174762a7656d23200ffa -->

## Notice ea5ab440900ab271811d5c2dc02a9de6e03a6956ac5727e85c11d76df5883d30

<!-- notice:ea5ab440900ab271811d5c2dc02a9de6e03a6956ac5727e85c11d76df5883d30 -->
Copyright (c) 2022 Steven Fackler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:ea5ab440900ab271811d5c2dc02a9de6e03a6956ac5727e85c11d76df5883d30 -->

## Notice ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055

<!-- notice:ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055 -->
Copyright (c) 2016--2017

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:ecc269ef87fd38a1d98e30bfac9ba964a9dbd9315c3770fed98d4d7cb5882055 -->

## Notice edd65bdd88957a205c47d53fa499eed8865a70320f0f03f6391668cb304ea376

<!-- notice:edd65bdd88957a205c47d53fa499eed8865a70320f0f03f6391668cb304ea376 -->

                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright 2024 Jacob Pratt et al.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

<!-- /notice:edd65bdd88957a205c47d53fa499eed8865a70320f0f03f6391668cb304ea376 -->

## Notice f2ad7982ddbfa8c45eb965315718c55b70b9cc311b49afacb50d5fe84173ae2c

<!-- notice:f2ad7982ddbfa8c45eb965315718c55b70b9cc311b49afacb50d5fe84173ae2c -->
Copyright (c) 2016 The rust-native-tls Developers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:f2ad7982ddbfa8c45eb965315718c55b70b9cc311b49afacb50d5fe84173ae2c -->

## Notice f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2

<!-- notice:f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2 -->
UNICODE LICENSE V3

COPYRIGHT AND PERMISSION NOTICE

Copyright © 2020-2024 Unicode, Inc.

NOTICE TO USER: Carefully read the following legal agreement. BY
DOWNLOADING, INSTALLING, COPYING OR OTHERWISE USING DATA FILES, AND/OR
SOFTWARE, YOU UNEQUIVOCALLY ACCEPT, AND AGREE TO BE BOUND BY, ALL OF THE
TERMS AND CONDITIONS OF THIS AGREEMENT. IF YOU DO NOT AGREE, DO NOT
DOWNLOAD, INSTALL, COPY, DISTRIBUTE OR USE THE DATA FILES OR SOFTWARE.

Permission is hereby granted, free of charge, to any person obtaining a
copy of data files and any associated documentation (the "Data Files") or
software and any associated documentation (the "Software") to deal in the
Data Files or Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, and/or sell
copies of the Data Files or Software, and to permit persons to whom the
Data Files or Software are furnished to do so, provided that either (a)
this copyright and permission notice appear with all copies of the Data
Files or Software, or (b) this copyright and permission notice appear in
associated Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF
THIRD PARTY RIGHTS.

IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE
BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES,
OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE DATA
FILES OR SOFTWARE.

Except as contained in this notice, the name of a copyright holder shall
not be used in advertising or otherwise to promote the sale, use or other
dealings in these Data Files or Software without prior written
authorization of the copyright holder.

SPDX-License-Identifier: Unicode-3.0

—

Portions of ICU4X may have been adapted from ICU4C and/or ICU4J.
ICU 1.8.1 to ICU 57.1 © 1995-2016 International Business Machines Corporation and others.

<!-- /notice:f367c1b8e1aa262435251e442901da4607b4650e0e63a026f5044473ecfb90f2 -->

## Notice f3d4287b4a21c5176fea2f9bd4ae800696004e2fb8e05cbc818be513f188a941

<!-- notice:f3d4287b4a21c5176fea2f9bd4ae800696004e2fb8e05cbc818be513f188a941 -->
Copyright 2011-2017 Google Inc.
          2013 Jack Lloyd
          2013-2014 Steven Fackler

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

<!-- /notice:f3d4287b4a21c5176fea2f9bd4ae800696004e2fb8e05cbc818be513f188a941 -->

## Notice f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7

<!-- notice:f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7 -->
Copyright (c) 2023 The Rust Project Developers

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:f51ac2c59a222f7476ce507ca879960e2b64ea64bb2786eefdbeb7b0b538d1b7 -->

## Notice f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1

<!-- notice:f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1 -->
UNICODE LICENSE V3

COPYRIGHT AND PERMISSION NOTICE

Copyright © 1991-2023 Unicode, Inc.

NOTICE TO USER: Carefully read the following legal agreement. BY
DOWNLOADING, INSTALLING, COPYING OR OTHERWISE USING DATA FILES, AND/OR
SOFTWARE, YOU UNEQUIVOCALLY ACCEPT, AND AGREE TO BE BOUND BY, ALL OF THE
TERMS AND CONDITIONS OF THIS AGREEMENT. IF YOU DO NOT AGREE, DO NOT
DOWNLOAD, INSTALL, COPY, DISTRIBUTE OR USE THE DATA FILES OR SOFTWARE.

Permission is hereby granted, free of charge, to any person obtaining a
copy of data files and any associated documentation (the "Data Files") or
software and any associated documentation (the "Software") to deal in the
Data Files or Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, and/or sell
copies of the Data Files or Software, and to permit persons to whom the
Data Files or Software are furnished to do so, provided that either (a)
this copyright and permission notice appear with all copies of the Data
Files or Software, or (b) this copyright and permission notice appear in
associated Documentation.

THE DATA FILES AND SOFTWARE ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT OF
THIRD PARTY RIGHTS.

IN NO EVENT SHALL THE COPYRIGHT HOLDER OR HOLDERS INCLUDED IN THIS NOTICE
BE LIABLE FOR ANY CLAIM, OR ANY SPECIAL INDIRECT OR CONSEQUENTIAL DAMAGES,
OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION,
ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THE DATA
FILES OR SOFTWARE.

Except as contained in this notice, the name of a copyright holder shall
not be used in advertising or otherwise to promote the sale, use or other
dealings in these Data Files or Software without prior written
authorization of the copyright holder.

<!-- /notice:f7db81051789b729fea528a63ec4c938fdcb93d9d61d97dc8cc2e9df6d47f2a1 -->

## Notice f7e8ab639afef15573680c97f796166835cbeb3865175882fea41c60d106b733

<!-- notice:f7e8ab639afef15573680c97f796166835cbeb3865175882fea41c60d106b733 -->
Copyright (c) 2018 Artyom Pavlov

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:f7e8ab639afef15573680c97f796166835cbeb3865175882fea41c60d106b733 -->

## Notice fac95e33eb175ff151cde39e3f7ad52292e6acf83db22bef30d3bfad417a8846

<!-- notice:fac95e33eb175ff151cde39e3f7ad52292e6acf83db22bef30d3bfad417a8846 -->
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: cookie-factory
Upstream-Contact: Geoffroy Couprie <geo.couprie@gmail.com> 
Source: https://github.com/rust-bakery/cookie-factory

Files: *
Copyright: 2017-2023 Geoffroy Couprie
License: MIT

<!-- /notice:fac95e33eb175ff151cde39e3f7ad52292e6acf83db22bef30d3bfad417a8846 -->

## Notice fea1d5bf3dd71605ce5d7d2ff695c1837e914c77195e523a86b5391716477960

<!-- notice:fea1d5bf3dd71605ce5d7d2ff695c1837e914c77195e523a86b5391716477960 -->
The MIT License (MIT)

Copyright (c) 2016 Prevoty, Inc. and jni-rs contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

<!-- /notice:fea1d5bf3dd71605ce5d7d2ff695c1837e914c77195e523a86b5391716477960 -->

## Notice ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2

<!-- notice:ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2 -->
Copyright (c) 2016 Amanieu d'Antras

Permission is hereby granted, free of charge, to any
person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the
Software without restriction, including without
limitation the rights to use, copy, modify, merge,
publish, distribute, sublicense, and/or sell copies of
the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice
shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR
IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

<!-- /notice:ff8f68cb076caf8cefe7a6430d4ac086ce6af2ca8ce2c4e5a2004d4552ef52a2 -->

## Notice ff92bed461f50338dd703a9ba9aee496a425957873df1d91192776e4bdf5dda7

<!-- notice:ff92bed461f50338dd703a9ba9aee496a425957873df1d91192776e4bdf5dda7 -->
LICENSE:
        This project is triple-licensed under the MIT License, the Apache
        License, Version 2.0, and the GNU Lesser General Public License,
        Version 2.1+.

AUTHORS-MIT:
        Permission is hereby granted, free of charge, to any person obtaining a
        copy of this software and associated documentation files (the
        "Software"), to deal in the Software without restriction, including
        without limitation the rights to use, copy, modify, merge, publish,
        distribute, sublicense, and/or sell copies of the Software, and to
        permit persons to whom the Software is furnished to do so, subject to
        the following conditions:

        The above copyright notice and this permission notice shall be included
        in all copies or substantial portions of the Software.

        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
        OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
        MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
        IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
        CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
        TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
        SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

AUTHORS-ASL:
        Licensed under the Apache License, Version 2.0 (the "License");
        you may not use this file except in compliance with the License.
        You may obtain a copy of the License at

                http://www.apache.org/licenses/LICENSE-2.0

        Unless required by applicable law or agreed to in writing, software
        distributed under the License is distributed on an "AS IS" BASIS,
        WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
        See the License for the specific language governing permissions and
        limitations under the License.

AUTHORS-LGPL:
        This program is free software; you can redistribute it and/or modify it
        under the terms of the GNU Lesser General Public License as published
        by the Free Software Foundation; either version 2.1 of the License, or
        (at your option) any later version.

        This program is distributed in the hope that it will be useful, but
        WITHOUT ANY WARRANTY; without even the implied warranty of
        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
        Lesser General Public License for more details.

        You should have received a copy of the GNU Lesser General Public License
        along with this program; If not, see <http://www.gnu.org/licenses/>.

COPYRIGHT: (ordered alphabetically)
        Copyright (C) 2017-2023 Red Hat, Inc.
        Copyright (C) 2019-2023 Microsoft Corporation
        Copyright (C) 2022-2023 David Rheinsberg

AUTHORS: (ordered alphabetically)
        Alex James <theracermaster@gmail.com>
        Ayush Singh <ayushsingh1325@gmail.com>
        Boris-Chengbiao Zhou <bobo1239@web.de>
        Bret Barkelew <bret@corthon.com>
        Christopher Zurcher <christopher.zurcher@microsoft.com>
        David Rheinsberg <david@readahead.eu>
        Dmitry Mostovenko <trueberserker@gmail.com>
        Hiroki Tokunaga <tokusan441@gmail.com>
        Joe Richey <joerichey@google.com>
        John Schock <joschock@microsoft.com>
        Michael Kubacki <michael.kubacki@microsoft.com>
        Oliver Smith-Denny <osde@microsoft.com>
        Richard Wiedenhöft <richard@wiedenhoeft.xyz>
        Rob Bradford <robert.bradford@intel.com>, <rbradford@rivosinc.com>
        Tom Gundersen <teg@jklm.no>
        Trevor Gross <tmgross@umich.edu>

<!-- /notice:ff92bed461f50338dd703a9ba9aee496a425957873df1d91192776e4bdf5dda7 -->

