"""Audited privacy-policy copy shared by the three website locales."""

EN_PRIVACY = {
    "title": "Privacy Policy — Mizan",
    "desc": "How the Mizan website and mobile application collect, use, share, retain and delete data.",
    "h1": "Privacy Policy",
    "updated": "Last updated: 29 October 2026",
    "intro": "This Privacy Policy applies to the Mizan website and Mizan mobile application (together, “Mizan”). It explains the data Mizan processes, why it is needed, the service providers involved, and your choices. Questions or privacy requests may be sent to {email}.",
    "sections": [
        ("Who is responsible for your data", [
            "The data controller for Mizan is Abdallah Hamada, an individual developer based in Istanbul, Türkiye. For any privacy request, including access, correction, deletion, restriction, objection or a copy of your data, contact {email}. We reply within 30 days.",
        ]),
        ("Data we process", [
            "Account and authentication data: name, email address, Mizan user ID, language and currency preferences. Email sign-in stores a salted password hash, not the password. Google Sign-In provides your name, email address and Google account identifier; Mizan does not receive your Google password.",
            "Financial records you choose to enter or confirm: accounts, balances, transactions, transfers, budgets, goals, recurring expenses, assets, categories, currencies, exchange-rate preferences and notes. Guest-mode records are stored on the device. Records are sent to Mizan’s backend for syncing after you sign in.",
            "Imported content: text that you deliberately share with Mizan is redacted before a structured transaction is saved; the original message text is not saved.",
            "AI requests and usage records: questions, instructions and relevant financial context are sent when you use an AI feature. Mizan stores operational usage records such as the model, request type, token counts, estimated cost and time, linked to your user ID; it does not store the AI request text in those usage records.",
            "Subscription data: plan, product, provider, status, renewal or expiry dates, store environment, and provider subscription or transaction identifiers. Payment-card numbers and bank credentials are not received or stored by Mizan.",
            "Support data: information you include when you contact support. Servers and payment providers may also process ordinary request, device, store and security metadata needed to deliver and protect their services.",
        ]),
        ("Data Mizan does not access", [
            "- Mizan does not connect to bank accounts and does not request bank passwords, card numbers, PINs or one-time codes.",
            "- The app does not read SMS messages or contacts and does not request location data.",
            "- The audited app and website contain no advertising SDK, advertising identifier use, third-party analytics or crash-reporting SDK.",
            "- Mizan does not sell personal or financial data and does not share it for targeted advertising.",
        ]),
        ("How data is used", [
            "To create and secure accounts; store and sync chosen records; calculate budgets, reports and forecasts; provide support; operate subscriptions and entitlements; prevent abuse; and maintain the service.",
            "AI content is processed only when you invoke an AI feature. Mizan does not use your financial records to create advertising profiles.",
            "The website uses only functional browser storage and language cookies for sign-in state, theme, language and checkout operation. Mizan does not use them for advertising or cross-site tracking.",
        ]),
        ("Service providers and sharing", [
            "- OpenAI processes the content needed to answer an AI request. Your name and email are not intentionally added to these requests.",
            "- Depending on the website checkout configuration, Paddle acts as merchant of record and processes checkout, tax, invoicing and subscription events, or Stripe processes hosted checkout and subscription events. These providers receive account and purchase details needed for billing; card details are entered with the provider, not Mizan.",
            "- Apple App Store and Google Play process in-app purchases, renewals, cancellations and refunds. RevenueCat receives Mizan’s authenticated user ID plus store, product and subscription-event data so Mizan can verify entitlement status across devices.",
            "- Google processes identity data when you choose Google Sign-In.",
            "- Netlify hosts the public website, Render hosts the backend API, and Neon provides the PostgreSQL database. These infrastructure providers process request, account and service data as needed to operate and secure Mizan.",
            "- Resend \u2014 sends transactional emails (email confirmation and password reset). Receives your email address and the message content.",
            "We only send emails needed to operate your account. We do not send marketing emails.",
            "Mizan may disclose information when legally required or to protect users, the service or legal rights. It does not share data with data brokers or advertisers.",
        ]),
        ("Security and deletion", [
            "Connections to the production website and API use HTTPS/TLS. Passwords are salted and hashed, authentication tokens are revocable, payment webhooks are signature-verified, and server-side secret keys are not embedded in the mobile app. No system can be guaranteed completely secure.",
            "You can permanently delete an account in Settings > Account > Delete account, or use the {delete_link}. On successful deletion, Mizan deletes the account and associated active-database records and clears account-linked local app records. Paddle subscriptions are cancelled by the deletion service first. Apple App Store, Google Play and legacy Stripe subscriptions must be cancelled with the provider; deleting Mizan does not by itself stop those providers from billing. Providers may retain transaction records under their own legal obligations.",
        ]),
        ("How long we keep data", [
            "- **Account and financial data:** kept while your account exists. When you delete your account, it is removed from our live database immediately and from backups within 30 days.",
            "- **Server logs** (user IDs and error messages, never your financial entries): up to 30 days.",
            "- **AI usage records** (model, token count and cost, never the text of your questions): kept while your account exists and deleted with it.",
            "- **AI requests:** sent to OpenAI to generate a reply. OpenAI may keep them for up to 30 days for abuse monitoring under its own policy.",
            "- **Billing records:** kept by our payment providers (Paddle, Stripe for earlier web subscriptions, and the app store you purchased through, where applicable) for as long as tax and accounting laws require.",
            "- **Support emails:** up to 2 years after the conversation ends.",
        ]),
        ("Your choices and rights", [
            "- Access and correction: view and edit your account and financial records in Mizan.",
            "- Export: export supported financial records from Settings > Export.",
            "- Delete: use the in-app control or the public deletion page. You may also contact {email}.",
            "- AI and imports: do not use the AI coach if you do not want selected content sent for AI processing; transaction-import sources can be disabled in Privacy settings.",
        ]),
        ("International transfers", [
            "Mizan is available worldwide. Your data is processed outside your country by the providers listed above, including in the European Union (Render, Frankfurt) and the United States (OpenAI). Where required, we rely on these providers’ data processing terms and standard contractual clauses.",
        ]),
        ("Your rights by region", [
            "- **EU, EEA and UK (GDPR / UK GDPR):** you have the right to access, correct, delete, restrict or object to processing, and to receive your data in a portable format (Settings → Export). We process data to provide the service you signed up for (contract), to keep it secure and prevent abuse (legitimate interests), and with your consent where we ask for it. You may complain to your local data protection authority.",
            "- **Türkiye (KVKK, Law No. 6698):** under Article 11 you have the right to learn whether your data is processed, request information about it, learn the purpose of processing and the third parties it is transferred to, request correction or deletion, object to a result produced solely by automated analysis that is against you, and claim compensation for damage caused by unlawful processing. You may also complain to the Personal Data Protection Board (KVKK).",
            "- **United States:** we do not sell your personal information or share it for cross-context behavioural advertising.",
            "- **Everywhere else:** you can use the same rights above by contacting {email}.",
        ]),
        ("Children", [
            "Mizan is intended for people aged 16 and over. We do not knowingly collect personal data from anyone under 16. If we learn that an account belongs to someone under 16, we will delete the account and its data. Users aged 16 and 17 should use Mizan with the knowledge of a parent or legal guardian.",
        ]),
        ("Changes and contact", [
            "This policy may change as Mizan changes. The effective date appears above, and material changes will be communicated where required.",
            "Privacy questions, deletion requests and complaints: {email}.",
        ]),
    ],
}

AR_PRIVACY = {
    "title": "سياسة الخصوصية — ميزان", "desc": "كيفية جمع بيانات موقع ميزان وتطبيقه واستخدامها ومشاركتها والاحتفاظ بها وحذفها.",
    "h1": "سياسة الخصوصية", "updated": "آخر تحديث: 29 أكتوبر 2026",
    "intro": "تسري سياسة الخصوصية هذه على موقع ميزان وتطبيق ميزان للهواتف (ويشار إليهما معًا بـ«ميزان»). وتوضح البيانات التي يعالجها ميزان، وسبب الحاجة إليها، ومقدمي الخدمات المشاركين، وخياراتك. أرسل أسئلة الخصوصية وطلباتها إلى {email}.",
    "sections": [
        ("من المسؤول عن بياناتك", [
            "المسؤول عن معالجة البيانات في ميزان هو عبدالله حمادة، وهو مطوّر فرد مقيم في إسطنبول، تركيا. لأي طلب يتعلق بالخصوصية، مثل الاطلاع على بياناتك أو تصحيحها أو حذفها أو تقييد معالجتها أو الاعتراض عليها أو الحصول على نسخة منها، راسلنا على {email}. نرد خلال 30 يومًا.",
        ]),
        ("البيانات التي نعالجها", [
            "بيانات الحساب والمصادقة: الاسم والبريد الإلكتروني ومعرّف مستخدم ميزان وتفضيلات اللغة والعملة. عند الدخول بالبريد نخزّن بصمة مملحة لكلمة المرور لا الكلمة نفسها. وعند استخدام Google نتلقى الاسم والبريد ومعرّف حساب Google، ولا نتلقى كلمة مرور Google.",
            "السجلات المالية التي تختار إدخالها أو تأكيدها: الحسابات والأرصدة والمعاملات والتحويلات والميزانيات والأهداف والمصروفات المتكررة والأصول والفئات والعملات وتفضيلات أسعار الصرف والملاحظات. تُحفظ سجلات وضع الضيف على الجهاز، وتُرسل السجلات إلى خادم ميزان للمزامنة بعد تسجيل الدخول.",
            "المحتوى المستورد: يُنقّح النص الذي تشاركه عمدًا مع ميزان قبل حفظ معاملة منظمة، ولا يُحفظ نص الرسالة الأصلي.",
            "طلبات الذكاء الاصطناعي وسجلات الاستخدام: تُرسل الأسئلة والتعليمات والسياق المالي اللازم عند استخدام ميزة ذكية. يحفظ ميزان سجلات تشغيل مثل النموذج ونوع الطلب وعدد الرموز والتكلفة التقديرية والوقت مرتبطة بمعرّف المستخدم، ولا يحفظ نص الطلب داخل تلك السجلات.",
            "بيانات الاشتراك: الباقة والمنتج والمزوّد والحالة وتواريخ التجديد أو الانتهاء وبيئة المتجر ومعرّفات الاشتراك أو المعاملة. لا يتلقى ميزان أرقام بطاقات الدفع أو بيانات الدخول البنكية ولا يخزنها.",
            "بيانات الدعم: ما ترسله عند التواصل مع الدعم. وقد تعالج الخوادم ومزوّدو الدفع بيانات الطلب والجهاز والمتجر والأمان العادية اللازمة لتقديم خدماتهم وحمايتها.",
        ]),
        ("بيانات لا يصل إليها ميزان", [
            "- لا يتصل ميزان بالحسابات البنكية ولا يطلب كلمات مرور البنوك أو أرقام البطاقات أو الأرقام السرية أو رموز التحقق.", "- لا يقرأ التطبيق الرسائل النصية أو جهات الاتصال ولا يطلب الموقع الجغرافي.",
            "- لا يتضمن التطبيق والموقع، وفق مراجعة الكود، حزمة إعلانات أو استخدامًا لمعرّفات الإعلانات أو تحليلات خارجية أو حزمة لتقارير الأعطال.", "- لا يبيع ميزان البيانات الشخصية أو المالية ولا يشاركها للإعلانات الموجهة.",
        ]),
        ("كيفية استخدام البيانات", [
            "لإنشاء الحسابات وتأمينها، وتخزين السجلات المختارة ومزامنتها، وحساب الميزانيات والتقارير والتوقعات، وتقديم الدعم، وتشغيل الاشتراكات والاستحقاقات، ومنع إساءة الاستخدام، وصيانة الخدمة.",
            "لا يُعالج محتوى الذكاء الاصطناعي إلا عند استدعائك ميزة ذكية. ولا يستخدم ميزان سجلاتك المالية لإنشاء ملفات إعلانية.",
            "يستخدم الموقع تخزين المتصفح الوظيفي وملفات لغة الارتباط فقط لحالة الدخول والمظهر واللغة وتشغيل الدفع، لا للإعلانات أو التتبع عبر المواقع.",
        ]),
        ("مقدمو الخدمات والمشاركة", [
            "- تعالج OpenAI المحتوى اللازم للإجابة عن طلب ذكي، ولا نضيف اسمك أو بريدك إلى هذه الطلبات عمدًا.",
            "- بحسب إعداد الدفع في الموقع، تعمل Paddle بصفتها البائع المسجّل وتعالج الدفع والضرائب والفواتير وأحداث الاشتراك، أو تعالج Stripe صفحة الدفع المستضافة وأحداث الاشتراك. تتلقى هذه الجهات تفاصيل الحساب والشراء اللازمة؛ وتُدخل البطاقة لديها لا لدى ميزان.",
            "- يعالج App Store وGoogle Play مشتريات التطبيق وتجديدها وإلغاءها وردّها. تتلقى RevenueCat معرّف مستخدم ميزان الموثق وبيانات المتجر والمنتج وأحداث الاشتراك للتحقق من الاستحقاق عبر الأجهزة.",
            "- تعالج Google بيانات الهوية عند اختيار تسجيل الدخول عبر Google.",
            "- يستضيف Netlify الموقع العام، ويستضيف Render الواجهة البرمجية، ويوفر Neon قاعدة بيانات PostgreSQL. وتعالج هذه الجهات بيانات الطلب والحساب والخدمة بالقدر اللازم لتشغيل ميزان وتأمينه.",
            "- Resend \u2014 يرسل رسائل البريد الخدمية (تأكيد البريد وإعادة تعيين كلمة المرور). يستلم بريدك الإلكتروني ومحتوى الرسالة.",
            "لا نرسل إلا الرسائل اللازمة لتشغيل حسابك، ولا نرسل رسائل تسويقية.",
            "قد يكشف ميزان معلومات عند إلزامه قانونًا أو لحماية المستخدمين أو الخدمة أو الحقوق القانونية، ولا يشاركها مع وسطاء البيانات أو المعلنين.",
        ]),
        ("الأمان والحذف", [
            "تستخدم اتصالات الموقع وواجهة الإنتاج HTTPS/TLS. كلمات المرور مملحة ومشفرة، ورموز المصادقة قابلة للإبطال، وتُتحقق تواقيع إشعارات الدفع، ولا توضع مفاتيح الخادم السرية داخل التطبيق. ولا يمكن ضمان أمان أي نظام بالكامل.",
            "يمكنك حذف الحساب نهائيًا من الإعدادات > الحساب > حذف الحساب، أو عبر {delete_link}. عند نجاح الحذف يمسح ميزان الحساب وسجلات قاعدة البيانات المرتبطة وبيانات التطبيق المحلية المرتبطة بالحساب. تُلغى اشتراكات Paddle أولًا. يجب إلغاء اشتراكات App Store وGoogle Play وStripe القديمة لدى المزوّد؛ حذف حساب ميزان وحده لا يوقف فوترة هؤلاء. وقد يحتفظ المزوّدون بسجلات المعاملات لالتزاماتهم القانونية.",
        ]),
        ("مدة الاحتفاظ بالبيانات", [
            "- **بيانات الحساب والبيانات المالية:** نحتفظ بها ما دام حسابك موجودًا. عند حذف حسابك، تُحذف فورًا من قاعدة البيانات الفعلية، ومن النسخ الاحتياطية خلال 30 يومًا.",
            "- **سجلات الخادم** (معرّفات المستخدمين ورسائل الأخطاء، ولا تتضمن أبدًا بياناتك المالية): حتى 30 يومًا.",
            "- **سجلات استخدام الذكاء الاصطناعي** (النموذج وعدد الرموز والتكلفة، ولا تتضمن أبدًا نص أسئلتك): نحتفظ بها ما دام حسابك موجودًا، وتُحذف معه.",
            "- **طلبات الذكاء الاصطناعي:** تُرسل إلى OpenAI لإنشاء الرد، وقد تحتفظ بها OpenAI لمدة تصل إلى 30 يومًا لمراقبة إساءة الاستخدام وفق سياستها الخاصة.",
            "- **سجلات الفواتير:** يحتفظ بها مزودو الدفع لدينا (Paddle، وStripe للاشتراكات القديمة عبر الموقع، ومتجر التطبيقات الذي اشتريت منه عند الاقتضاء) طوال المدة التي تفرضها قوانين الضرائب والمحاسبة.",
            "- **رسائل الدعم:** حتى سنتين بعد انتهاء المراسلة.",
        ]),
        ("خياراتك وحقوقك", [
            "- الوصول والتصحيح: اعرض بيانات حسابك وسجلاتك المالية وعدّلها داخل ميزان.", "- التصدير: صدّر السجلات المالية المدعومة من الإعدادات > تصدير.",
            "- الحذف: استخدم أداة التطبيق أو صفحة الحذف العامة، أو تواصل عبر {email}.", "- الذكاء الاصطناعي والاستيراد: لا تستخدم المساعد الذكي إن لم ترد إرسال المحتوى المختار للمعالجة، ويمكن تعطيل مصادر الاستيراد من إعدادات الخصوصية.",
        ]),
        ("نقل البيانات خارج بلدك", [
            "ميزان متاح في جميع أنحاء العالم. تُعالج بياناتك خارج بلدك لدى مزودي الخدمة المذكورين أعلاه، بما في ذلك الاتحاد الأوروبي (Render، فرانكفورت) والولايات المتحدة (OpenAI). وعند الاقتضاء، نعتمد على شروط معالجة البيانات لدى هؤلاء المزودين والبنود التعاقدية القياسية.",
        ]),
        ("حقوقك حسب منطقتك", [
            "- **الاتحاد الأوروبي والمنطقة الاقتصادية الأوروبية والمملكة المتحدة (GDPR):** يحق لك الاطلاع على بياناتك وتصحيحها وحذفها وتقييد معالجتها أو الاعتراض عليها، والحصول عليها بصيغة قابلة للنقل (الإعدادات ← تصدير). نعالج البيانات لتقديم الخدمة التي اشتركت فيها (تنفيذ العقد)، وللحفاظ على أمانها ومنع إساءة الاستخدام (المصلحة المشروعة)، وبموافقتك حين نطلبها. ويحق لك تقديم شكوى إلى هيئة حماية البيانات في بلدك.",
            "- **تركيا (قانون حماية البيانات الشخصية KVKK رقم 6698):** بموجب المادة 11 يحق لك معرفة ما إذا كانت بياناتك تُعالج، وطلب معلومات عنها، ومعرفة الغرض من معالجتها والأطراف التي نُقلت إليها، وطلب تصحيحها أو حذفها، والاعتراض على أي نتيجة تضرّك ناتجة حصريًا عن تحليل آلي، والمطالبة بالتعويض عن الضرر الناتج عن المعالجة غير المشروعة. ويحق لك أيضًا تقديم شكوى إلى هيئة حماية البيانات الشخصية التركية.",
            "- **الولايات المتحدة:** لا نبيع معلوماتك الشخصية ولا نشاركها لأغراض الإعلانات السلوكية.",
            "- **بقية الدول:** يمكنك ممارسة الحقوق نفسها المذكورة أعلاه بمراسلة {email}.",
        ]),
        ("الأطفال", ["ميزان مخصص لمن تبلغ أعمارهم 16 عامًا فأكثر. لا نجمع عن علم أي بيانات شخصية ممن تقل أعمارهم عن 16 عامًا، وإذا علمنا أن حسابًا يعود لشخص دون 16 عامًا فسنحذف الحساب وبياناته. وينبغي لمن تبلغ أعمارهم 16 و17 عامًا استخدام ميزان بعلم أحد الوالدين أو الولي القانوني." ]),
        ("التغييرات والتواصل", ["قد تتغير هذه السياسة مع تغير ميزان. يظهر تاريخ السريان أعلاه، وسنبلغ عن التغييرات الجوهرية حيث يلزم.", "لأسئلة الخصوصية وطلبات الحذف والشكاوى: {email}."]),
    ],
}

TR_PRIVACY = {
    "title": "Gizlilik Politikası — Mizan", "desc": "Mizan web sitesi ve mobil uygulamasının verileri nasıl topladığı, kullandığı, paylaştığı, sakladığı ve sildiği.",
    "h1": "Gizlilik Politikası", "updated": "Son güncelleme: 29 Ekim 2026",
    "intro": "Bu Gizlilik Politikası Mizan web sitesi ve Mizan mobil uygulaması (birlikte “Mizan”) için geçerlidir. Mizan’ın işlediği verileri, bunların neden gerekli olduğunu, hizmet sağlayıcıları ve seçimlerinizi açıklar. Sorularınızı ve gizlilik taleplerinizi {email} adresine gönderebilirsiniz.",
    "sections": [
        ("Verilerinizden kim sorumlu", [
            "Mizan için veri sorumlusu, İstanbul, Türkiye'de yaşayan bireysel geliştirici Abdallah Hamada'dır. Erişim, düzeltme, silme, kısıtlama, itiraz veya verilerinizin bir kopyasını alma dahil her türlü gizlilik talebiniz için {email} adresine yazabilirsiniz. Taleplere 30 gün içinde yanıt veririz.",
        ]),
        ("İşlediğimiz veriler", [
            "Hesap ve kimlik doğrulama verileri: ad, e-posta adresi, Mizan kullanıcı kimliği, dil ve para birimi tercihleri. E-posta ile girişte parolanın kendisi değil, tuzlanmış özeti saklanır. Google ile girişte adınız, e-postanız ve Google hesap kimliğiniz alınır; Google parolanız alınmaz.",
            "Girmeyi veya onaylamayı seçtiğiniz finans kayıtları: hesaplar, bakiyeler, işlemler, transferler, bütçeler, hedefler, yinelenen giderler, varlıklar, kategoriler, para birimleri, kur tercihleri ve notlar. Misafir verileri cihazda tutulur; giriş yaptıktan sonra kayıtlar eşitleme için Mizan sunucusuna gönderilir.",
            "İçe aktarılan içerik: bilerek paylaştığınız metin, yapılandırılmış işlem kaydedilmeden önce hassas bilgilerden arındırılır; özgün mesaj metni saklanmaz.",
            "Yapay zekâ istekleri ve kullanım kayıtları: bir AI özelliğini kullandığınızda soru, talimat ve gerekli finans bağlamı gönderilir. Model, istek türü, token sayıları, tahmini maliyet ve zaman gibi işletim kayıtları kullanıcı kimliğinizle tutulur; istek metni bu kullanım kayıtlarında saklanmaz.",
            "Abonelik verileri: plan, ürün, sağlayıcı, durum, yenileme veya bitiş tarihleri, mağaza ortamı ve sağlayıcı abonelik/işlem kimlikleri. Kart numarası ve banka giriş bilgileri Mizan tarafından alınmaz veya saklanmaz.",
            "Destek verileri: desteğe yazarken verdiğiniz bilgiler. Sunucular ve ödeme sağlayıcıları hizmeti sunmak ve korumak için olağan istek, cihaz, mağaza ve güvenlik meta verilerini de işleyebilir.",
        ]),
        ("Mizan’ın erişmediği veriler", ["- Mizan banka hesabına bağlanmaz; banka parolası, kart numarası, PIN veya tek kullanımlık kod istemez.", "- Uygulama SMS’leri veya kişileri okumaz ve konum istemez.", "- Denetlenen uygulama ve sitede reklam SDK’sı, reklam kimliği kullanımı, üçüncü taraf analiz veya çökme raporlama SDK’sı yoktur.", "- Mizan kişisel veya finansal veriyi satmaz ve hedefli reklam için paylaşmaz."]),
        ("Verileri kullanma amaçlarımız", ["Hesap oluşturmak ve korumak; seçilen kayıtları saklamak ve eşitlemek; bütçe, rapor ve tahmin hesaplamak; destek vermek; abonelik ve hakları işletmek; kötüye kullanımı önlemek ve hizmeti sürdürmek.", "AI içeriği yalnızca siz bir AI özelliğini çağırdığınızda işlenir. Finans kayıtlarınız reklam profili oluşturmak için kullanılmaz.", "Site yalnızca oturum, tema, dil ve ödeme işlevleri için işlevsel tarayıcı depolaması ve dil çerezleri kullanır; reklam veya siteler arası izleme için kullanmaz."]),
        ("Hizmet sağlayıcılar ve paylaşım", [
            "- OpenAI, AI isteğini yanıtlamak için gereken içeriği işler. Adınız ve e-postanız bu isteklere bilerek eklenmez.",
            "- Web ödeme yapılandırmasına göre Paddle kayıtlı satıcı olarak ödeme, vergi, fatura ve abonelik olaylarını işler veya Stripe barındırılan ödeme ve abonelik olaylarını işler. Gerekli hesap ve satın alma ayrıntıları sağlayıcıya gider; kart bilgisi Mizan’a değil sağlayıcıya girilir.",
            "- Apple App Store ve Google Play uygulama içi satın alma, yenileme, iptal ve iadeleri işler. RevenueCat, hak durumunu cihazlar arasında doğrulamak için doğrulanmış Mizan kullanıcı kimliğini ve mağaza, ürün ve abonelik olayı verilerini alır.",
            "- Google ile girişi seçerseniz kimlik verilerini Google işler.",
            "- Netlify genel web sitesini, Render arka uç API’sini barındırır; Neon ise PostgreSQL veritabanını sağlar. Bu altyapı sağlayıcıları Mizan’ı işletmek ve korumak için gereken istek, hesap ve hizmet verilerini işler.",
            "- Resend \u2014 işlemsel e-postaları (e-posta doğrulama ve şifre sıfırlama) gönderir. E-posta adresinizi ve mesaj içeriğini alır.",
            "Yalnızca hesabınızın çalışması için gerekli e-postaları göndeririz. Pazarlama e-postası göndermeyiz.",
            "Mizan, yasal zorunluluk halinde veya kullanıcıları, hizmeti ya da hakları korumak için bilgi açıklayabilir; veri brokerları veya reklamverenlerle paylaşmaz.",
        ]),
        ("Güvenlik ve silme", [
            "Üretim sitesi ve API bağlantıları HTTPS/TLS kullanır. Parolalar tuzlanıp özetlenir, kimlik belirteçleri iptal edilebilir, ödeme webhook imzaları doğrulanır ve sunucu sırları uygulamaya gömülmez. Hiçbir sistemin tamamen güvenli olduğu garanti edilemez.",
            "Hesabı Ayarlar > Hesap > Hesabı sil yolundan veya {delete_link} üzerinden kalıcı silebilirsiniz. Başarılı silmede hesap, ilişkili etkin veritabanı kayıtları ve hesaba bağlı yerel kayıtlar silinir. Önce Paddle abonelikleri iptal edilir. App Store, Google Play ve eski Stripe abonelikleri sağlayıcıda iptal edilmelidir; Mizan hesabını silmek bunların faturalamasını tek başına durdurmaz. Sağlayıcılar yasal yükümlülükleri için işlem kayıtlarını tutabilir.",
        ]),
        ("Verileri ne kadar süre saklıyoruz", [
            "- **Hesap ve finansal veriler:** Hesabınız var olduğu sürece saklanır. Hesabınızı sildiğinizde canlı veritabanımızdan hemen, yedeklerden ise 30 gün içinde silinir.",
            "- **Sunucu kayıtları** (kullanıcı kimlikleri ve hata mesajları; finansal kayıtlarınız asla yer almaz): en fazla 30 gün.",
            "- **Yapay zekâ kullanım kayıtları** (model, token sayısı ve maliyet; sorularınızın metni asla yer almaz): hesabınız var olduğu sürece saklanır ve hesapla birlikte silinir.",
            "- **Yapay zekâ istekleri:** Yanıt oluşturmak için OpenAI'ye gönderilir. OpenAI, kendi politikası kapsamında kötüye kullanımı izlemek amacıyla bunları 30 güne kadar saklayabilir.",
            "- **Fatura kayıtları:** Ödeme sağlayıcılarımız (Paddle, eski web abonelikleri için Stripe ve uygun durumlarda satın alım yaptığınız uygulama mağazası) tarafından vergi ve muhasebe mevzuatının gerektirdiği süre boyunca saklanır.",
            "- **Destek e-postaları:** Yazışmanın sona ermesinden itibaren en fazla 2 yıl.",
        ]),
        ("Seçimleriniz ve haklarınız", ["- Erişim ve düzeltme: hesap ve finans kayıtlarını Mizan’da görüntüleyip düzenleyin.", "- Dışa aktarma: desteklenen finans kayıtlarını Ayarlar > Dışa aktar bölümünden alın.", "- Silme: uygulama içi denetimi veya herkese açık silme sayfasını kullanın ya da {email} adresine yazın.", "- AI ve içe aktarma: seçilen içeriğin AI işlemesine gitmesini istemiyorsanız AI koçunu kullanmayın; içe aktarma kaynakları Gizlilik ayarlarında kapatılabilir.",]),
        ("Yurt dışına aktarım", [
            "Mizan dünya genelinde kullanılabilir. Verileriniz, yukarıda sayılan hizmet sağlayıcılar tarafından ülkeniz dışında işlenir; bunlara Avrupa Birliği (Render, Frankfurt) ve Amerika Birleşik Devletleri (OpenAI) dahildir. Gerektiği durumlarda bu sağlayıcıların veri işleme koşullarına ve standart sözleşme hükümlerine dayanırız.",
        ]),
        ("Bölgenize göre haklarınız", [
            "- **AB, AEA ve Birleşik Krallık (GDPR / UK GDPR):** Verilerinize erişme, bunları düzeltme, silme, işlenmesini kısıtlama veya işlenmesine itiraz etme ve verilerinizi taşınabilir bir biçimde alma (Ayarlar → Dışa aktar) hakkına sahipsiniz. Verileri; kaydolduğunuz hizmeti sunmak (sözleşme), hizmeti güvende tutmak ve kötüye kullanımı önlemek (meşru menfaat) ve talep ettiğimiz durumlarda açık rızanıza dayanarak işleriz. Bulunduğunuz ülkenin veri koruma otoritesine şikâyette bulunabilirsiniz.",
            "- **Türkiye (6698 sayılı KVKK):** 11. madde kapsamında; kişisel verilerinizin işlenip işlenmediğini öğrenme, buna ilişkin bilgi talep etme, işlenme amacını ve aktarıldığı üçüncü kişileri öğrenme, düzeltilmesini veya silinmesini isteme, münhasıran otomatik sistemlerle analiz edilmesi sonucu aleyhinize bir sonuç çıkmasına itiraz etme ve kanuna aykırı işleme nedeniyle zarara uğramanız hâlinde zararın giderilmesini talep etme haklarına sahipsiniz. Ayrıca Kişisel Verileri Koruma Kurulu'na şikâyette bulunabilirsiniz.",
            "- **Amerika Birleşik Devletleri:** Kişisel bilgilerinizi satmayız ve davranışsal reklamcılık amacıyla paylaşmayız.",
            "- **Diğer tüm ülkeler:** Yukarıdaki hakları {email} adresine yazarak kullanabilirsiniz.",
        ]),
        ("Çocuklar", ["Mizan, 16 yaş ve üzeri kişilere yöneliktir. 16 yaşından küçük kişilerden bilerek kişisel veri toplamayız; bir hesabın 16 yaşından küçük birine ait olduğunu öğrenirsek hesabı ve verilerini sileriz. 16 ve 17 yaşındaki kullanıcıların Mizan'ı ebeveynlerinin veya yasal vasilerinin bilgisi dahilinde kullanmaları gerekir."]),
        ("Değişiklikler ve iletişim", ["Mizan değiştikçe bu politika değişebilir. Yürürlük tarihi yukarıdadır; önemli değişiklikler gerektiğinde bildirilir.", "Gizlilik soruları, silme talepleri ve şikâyetler: {email}."]),
    ],
}
