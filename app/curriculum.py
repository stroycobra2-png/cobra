import json

LEVELS = [
    ('A1', 'Başlangıç', 'Temel günlük ifadeler, basit cümleler ve tanışma.'),
    ('A2', 'Temel', 'Günlük yaşam, geçmiş-gelecek anlatımı ve temel etkileşim.'),
    ('B1', 'Orta', 'Bağımsız iletişim, fikir belirtme ve daha uzun metinler.'),
    ('B2', 'Orta-Üst', 'Akıcı iletişim, tartışma, gelişmiş dilbilgisi ve yazma.'),
    ('C1', 'İleri', 'Akademik/profesyonel kullanım, nüans ve karmaşık metinler.'),
    ('C2', 'Ustalık', 'Doğal, esnek, stil sahibi ve ileri düzey İngilizce.'),
]

TOPICS = {
    'A1': [
        ('Selamlaşma', 'to be: am/is/are', [('hello','merhaba'),('good morning','günaydın'),('goodbye','hoşça kal'),('please','lütfen'),('thanks','teşekkürler')], 'Hello, I am Deniz. Nice to meet you.'),
        ('Kendini Tanıtma', 'I am / My name is / I am from', [('name','isim'),('student','öğrenci'),('country','ülke'),('city','şehir'),('meet','tanışmak')], 'My name is Emma and I am from London.'),
        ('Sayılar ve Yaş', 'How old are you?', [('one','bir'),('ten','on'),('twenty','yirmi'),('hundred','yüz'),('age','yaş')], 'I am sixteen years old.'),
        ('Aile', 'possessive adjectives: my/your/his/her', [('mother','anne'),('father','baba'),('sister','kız kardeş'),('brother','erkek kardeş'),('family','aile')], 'This is my sister. Her name is Lily.'),
        ('Günlük Rutin', 'present simple', [('wake up','uyanmak'),('school','okul'),('eat','yemek'),('study','çalışmak'),('sleep','uyumak')], 'I wake up at seven and go to school.'),
        ('Yiyecek ve İçecek', 'like / do not like', [('bread','ekmek'),('water','su'),('apple','elma'),('breakfast','kahvaltı'),('hungry','aç')], 'I like apples, but I do not like coffee.'),
        ('Ev ve Odalar', 'there is / there are', [('house','ev'),('room','oda'),('kitchen','mutfak'),('bedroom','yatak odası'),('table','masa')], 'There is a table in the kitchen.'),
        ('Şehir ve Yönler', 'imperatives and prepositions', [('street','sokak'),('left','sol'),('right','sağ'),('near','yakın'),('station','istasyon')], 'Turn left. The station is near the bank.'),
        ('Hobiler ve Yetenekler', 'can / cannot', [('swim','yüzmek'),('read','okumak'),('music','müzik'),('football','futbol'),('draw','çizmek')], 'I can swim and draw, but I cannot drive.'),
        ('A1 Genel Tekrar', 'present simple + be + can', [('always','her zaman'),('sometimes','bazen'),('today','bugün'),('friend','arkadaş'),('learn','öğrenmek')], 'Today I learn English with my friend.'),
    ],
    'A2': [
        ('Geçen Hafta Sonu', 'past simple', [('visited','ziyaret etti'),('watched','izledi'),('went','gitti'),('yesterday','dün'),('weekend','hafta sonu')], 'Last weekend I went to the cinema with my friends.'),
        ('Seyahat', 'past simple questions', [('ticket','bilet'),('airport','havaalanı'),('hotel','otel'),('journey','yolculuk'),('luggage','bagaj')], 'We bought our tickets before we went to the airport.'),
        ('Alışveriş', 'countable/uncountable + some/any', [('price','fiyat'),('cheap','ucuz'),('expensive','pahalı'),('size','beden'),('cash','nakit')], 'Do you have this shirt in a larger size?'),
        ('Sağlık', 'should / should not', [('headache','baş ağrısı'),('doctor','doktor'),('medicine','ilaç'),('rest','dinlenmek'),('healthy','sağlıklı')], 'You should rest and drink more water.'),
        ('Gelecek Planları', 'be going to', [('plan','plan'),('tomorrow','yarın'),('holiday','tatil'),('visit','ziyaret etmek'),('future','gelecek')], 'I am going to visit Ankara next month.'),
        ('Karşılaştırmalar', 'comparatives / superlatives', [('bigger','daha büyük'),('faster','daha hızlı'),('best','en iyi'),('than','-den daha'),('interesting','ilginç')], 'This book is more interesting than the other one.'),
        ('Deneyimler', 'present perfect: ever/never', [('experience','deneyim'),('ever','hiç'),('never','asla/hiç'),('already','çoktan'),('yet','henüz')], 'I have never travelled by ship.'),
        ('Kurallar ve Zorunluluk', 'must / have to', [('rule','kural'),('must','zorunda'),('uniform','üniforma'),('permission','izin'),('careful','dikkatli')], 'Students have to arrive before nine.'),
        ('Davetler', 'would like / could', [('invite','davet etmek'),('party','parti'),('available','müsait'),('join','katılmak'),('perhaps','belki')], 'Would you like to join us for dinner?'),
        ('A2 Genel Tekrar', 'past + future + present perfect', [('improve','geliştirmek'),('conversation','konuşma'),('practice','pratik'),('recently','yakın zamanda'),('goal','hedef')], 'I have recently started practising English every day.'),
    ],
    'B1': [
        ('Deneyim ve Sonuç', 'present perfect vs past simple', [('achievement','başarı'),('recent','yakın zamandaki'),('result','sonuç'),('since','-den beri'),('for','boyunca')], 'I have studied English for three years, and I passed an exam last June.'),
        ('Hikâye Anlatma', 'past continuous + past simple', [('suddenly','aniden'),('while','-iken'),('event','olay'),('notice','fark etmek'),('happen','olmak')], 'I was walking home when I suddenly noticed a lost dog.'),
        ('Fikir Belirtme', 'opinion language', [('opinion','görüş'),('agree','katılmak'),('disagree','katılmamak'),('reason','neden'),('however','ancak')], 'In my opinion, online learning is useful; however, it requires discipline.'),
        ('İş ve Eğitim', 'gerunds and infinitives', [('career','kariyer'),('skill','beceri'),('apply','başvurmak'),('degree','diploma'),('training','eğitim')], 'I decided to apply for a course to improve my communication skills.'),
        ('Çevre', 'first conditional', [('environment','çevre'),('recycle','geri dönüştürmek'),('waste','atık'),('climate','iklim'),('protect','korumak')], 'If we recycle more, we will reduce waste.'),
        ('Medya', 'reported statements introduction', [('headline','manşet'),('source','kaynak'),('report','haber vermek'),('social media','sosyal medya'),('reliable','güvenilir')], 'The reporter said that the story was based on reliable sources.'),
        ('Koşullar', 'second conditional', [('imagine','hayal etmek'),('choice','seçim'),('possible','mümkün'),('decision','karar'),('opportunity','fırsat')], 'If I had more free time, I would learn another language.'),
        ('İnsanları ve Nesneleri Tanımlama', 'relative clauses', [('person','kişi'),('which','ki'),('who','kim/kişi için'),('describe','tanımlamak'),('feature','özellik')], 'A teacher is someone who helps people learn.'),
        ('Süreçler', 'passive voice introduction', [('produce','üretmek'),('process','süreç'),('manufacture','imal etmek'),('deliver','teslim etmek'),('material','malzeme')], 'Coffee is grown in many countries and is exported around the world.'),
        ('B1 Genel Tekrar', 'B1 mixed grammar', [('fluency','akıcılık'),('confidence','özgüven'),('express','ifade etmek'),('detail','detay'),('progress','ilerleme')], 'My confidence has improved because I practise speaking regularly.'),
    ],
    'B2': [
        ('Aktarılan Konuşma', 'reported speech', [('claim','iddia etmek'),('mention','bahsetmek'),('announce','duyurmak'),('statement','açıklama'),('according to','-e göre')], 'She explained that the project would be completed the following week.'),
        ('İleri Koşullar', 'mixed conditionals', [('consequence','sonuç'),('alternative','alternatif'),('regret','pişmanlık'),('otherwise','aksi halde'),('circumstance','koşul')], 'If I had accepted that offer, I might be living abroad now.'),
        ('Collocations', 'natural word combinations', [('make progress','ilerleme kaydetmek'),('take responsibility','sorumluluk almak'),('strong argument','güçlü argüman'),('deeply concerned','derinden endişeli'),('highly effective','son derece etkili')], 'The team made significant progress after taking responsibility for the problem.'),
        ('Phrasal Verbs', 'multi-word verbs', [('carry out','gerçekleştirmek'),('point out','belirtmek'),('come across','rastlamak'),('work out','çözmek'),('bring up','gündeme getirmek')], 'The researchers carried out a study and pointed out several risks.'),
        ('Tartışma', 'concession and contrast', [('nevertheless','yine de'),('whereas','oysa'),('despite','-e rağmen'),('argument','argüman'),('evidence','kanıt')], 'The proposal is expensive; nevertheless, the evidence suggests it may work.'),
        ('Resmî Yazışma', 'formal register', [('regarding','hakkında'),('request','talep'),('further information','ek bilgi'),('sincerely','saygılarımla'),('enquiry','bilgi talebi')], 'I am writing regarding your recent announcement and would appreciate further information.'),
        ('İleri Passive', 'passive reporting structures', [('believed','inanılmak'),('estimated','tahmin edilmek'),('expected','beklenmek'),('reported','bildirilmek'),('considered','kabul edilmek')], 'The new system is expected to reduce waiting times significantly.'),
        ('Teknoloji ve Toplum', 'complex cause/effect', [('innovation','yenilik'),('privacy','mahremiyet'),('automation','otomasyon'),('impact','etki'),('ethical','etik')], 'Automation can improve efficiency, although its social impact must be considered.'),
        ('Kültür ve Perspektif', 'discourse markers', [('perspective','bakış açısı'),('tradition','gelenek'),('identity','kimlik'),('diverse','çeşitli'),('interpret','yorumlamak')], 'Cultural identity is shaped by tradition, language and personal experience.'),
        ('B2 Genel Tekrar', 'B2 mixed structures', [('accurate','doğru'),('coherent','tutarlı'),('advanced','ileri'),('spontaneous','doğaçlama'),('range','çeşitlilik')], 'A B2 speaker can express ideas clearly and respond relatively spontaneously.'),
    ],
    'C1': [
        ('Akademik Kelime', 'academic register', [('substantial','kayda değer'),('derive','türetmek/elde etmek'),('framework','çerçeve'),('assumption','varsayım'),('evaluate','değerlendirmek')], 'The findings provide substantial evidence for evaluating the existing framework.'),
        ('Hedging ve Temkinli Dil', 'may/might/tend to/appears to', [('apparently','görünüşe göre'),('arguably','tartışmalı biçimde'),('potentially','potansiyel olarak'),('tend to','eğiliminde olmak'),('suggest','öne sürmek')], 'The data appears to suggest that the policy may have had a limited effect.'),
        ('Karmaşık Cümleler', 'subordination and clause control', [('whereby','vasıtasıyla'),('provided that','şartıyla'),('insofar as','-dığı ölçüde'),('notwithstanding','-e rağmen'),('thereby','böylece')], 'The system adapts to demand, thereby reducing unnecessary resource use.'),
        ('Sunum Dili', 'signposting', [('outline','ana hatlarını vermek'),('highlight','vurgulamak'),('turn to','konuya geçmek'),('summarise','özetlemek'),('implication','çıkarım')], 'I will first outline the issue, then highlight its main implications.'),
        ('Raporlama', 'objective report style', [('finding','bulgu'),('recommendation','öneri'),('limitation','sınırlılık'),('methodology','yöntem'),('outcome','sonuç')], 'The report identifies three limitations and proposes two practical recommendations.'),
        ('Argümantasyon', 'counterargument and rebuttal', [('premise','öncül'),('counterargument','karşı argüman'),('valid','geçerli'),('undermine','zayıflatmak'),('justify','gerekçelendirmek')], 'Although the counterargument is valid, it does not undermine the central premise.'),
        ('Register', 'formal/informal/style choice', [('register','dil düzeyi'),('appropriate','uygun'),('concise','özlü'),('colloquial','gündelik'),('tone','ton')], 'A concise formal tone is generally more appropriate in professional reports.'),
        ('Çıkarım ve İma', 'inference', [('infer','çıkarım yapmak'),('implicit','örtük'),('nuance','ince anlam'),('context','bağlam'),('interpretation','yorum')], 'The author never states the conclusion directly; the reader must infer it from context.'),
        ('Sentez', 'synthesising multiple sources', [('synthesis','sentez'),('contrast','karşılaştırmak'),('integrate','bütünleştirmek'),('source','kaynak'),('consensus','uzlaşı')], 'A strong synthesis integrates several sources rather than summarising them separately.'),
        ('C1 Genel Tekrar', 'C1 control and precision', [('precision','kesinlik'),('flexibility','esneklik'),('sophisticated','gelişmiş'),('cohesion','bağlaşıklık'),('subtle','ince')], 'At C1 level, speakers can communicate complex ideas with considerable precision and flexibility.'),
    ],
    'C2': [
        ('Nüans ve İnce Anlam', 'semantic nuance', [('meticulous','son derece titiz'),('ambiguous','belirsiz/çift anlamlı'),('subtle','ince'),('connotation','çağrışım'),('distinction','ayrım')], 'The distinction is subtle, yet the connotations of the two expressions are markedly different.'),
        ('Deyimler', 'idiomatic control', [('a double-edged sword','iki ucu keskin kılıç'),('the tip of the iceberg','buzdağının görünen kısmı'),('read between the lines','satır aralarını okumak'),('by and large','genel olarak'),('in a nutshell','kısaca')], 'By and large, the policy succeeded, although that is only the tip of the iceberg.'),
        ('Retorik', 'rhetorical devices', [('rhetoric','retorik'),('analogy','benzetme'),('emphasis','vurgu'),('parallelism','paralellik'),('persuasive','ikna edici')], 'The speaker used parallelism and analogy to make the argument more persuasive.'),
        ('Stil Kontrolü', 'stylistic transformation', [('eloquent','etkileyici ve akıcı'),('succinct','özlü'),('verbose','gereğinden uzun'),('refine','inceltmek/geliştirmek'),('craft','özenle oluşturmak')], 'The editor refined the paragraph until it was succinct without losing its nuance.'),
        ('İroni ve Alt Metin', 'pragmatics and implied meaning', [('irony','ironi'),('sarcasm','alay'),('subtext','alt metin'),('literal','kelimesi kelimesine'),('intention','niyet')], 'A literal interpretation misses the irony and the social intention behind the remark.'),
        ('İleri Collocations', 'lexical sophistication', [('fundamentally flawed','temelden kusurlu'),('broad consensus','geniş uzlaşı'),('deep-seated','köklü'),('compelling evidence','ikna edici kanıt'),('utterly remarkable','tam anlamıyla dikkat çekici')], 'The proposal attracted broad consensus despite concerns about a deep-seated structural problem.'),
        ('Edebi Analiz', 'literary language', [('motif','motif'),('narrative','anlatı'),('symbolism','sembolizm'),('perspective','bakış açısı'),('ambiguity','belirsizlik')], 'The recurring motif reinforces the narrative ambiguity and shifts the reader’s perspective.'),
        ('Müzakere', 'diplomatic language', [('concession','taviz'),('mutual','karşılıklı'),('feasible','uygulanabilir'),('compromise','uzlaşma'),('stipulation','koşul')], 'A mutually acceptable compromise may be feasible if both sides reconsider one stipulation.'),
        ('Editörlük', 'precision editing', [('redundant','gereksiz tekrar içeren'),('clarity','açıklık'),('cohesive','bütünlüklü'),('revise','gözden geçirmek'),('wording','ifade biçimi')], 'The revised wording is more cohesive and removes several redundant phrases.'),
        ('C2 Genel Tekrar', 'mastery and flexible control', [('mastery','ustalık'),('effortless','zahmetsiz'),('idiomatic','deyimsel/doğal'),('adapt','uyarlamak'),('precision','kesinlik')], 'C2 mastery involves adapting language almost effortlessly to purpose, audience and context.'),
    ],
}


def make_quiz(title, grammar, vocab, example):
    first_word, first_tr = vocab[0]
    wrongs = [v[1] for v in vocab[1:4]]
    while len(wrongs) < 3:
        wrongs.append('farklı anlam')
    q1 = {
        'question': f'“{first_word}” kelimesinin en uygun Türkçe karşılığı hangisidir?',
        'options': [first_tr, wrongs[0], wrongs[1], wrongs[2]],
        'correct': 0,
        'skill': 'vocabulary'
    }
    q2 = {
        'question': f'Bu dersin ana dilbilgisi konusu hangisidir?',
        'options': [grammar, 'Sadece telaffuz', 'Sadece yazım', 'Matematiksel ifadeler'],
        'correct': 0,
        'skill': 'grammar'
    }
    q3 = {
        'question': 'Aşağıdaki cümle bu dersin bağlamına uygun mudur?\n' + example,
        'options': ['Evet', 'Hayır', 'Cümle İngilizce değil', 'Belirlenemez'],
        'correct': 0,
        'skill': 'reading'
    }
    return json.dumps([q1, q2, q3], ensure_ascii=False)


def generate_lessons():
    """Her CEFR seviyesi için tam 50 ders üretir.

    Yapı:
    - İlk 10 ders, önceki sürümdeki ana derslerle aynı position değerlerini korur.
      Böylece eski kullanıcıların ders ilerlemesi mümkün olduğunca korunur.
    - Sonraki 40 ders, 10 ana ünitenin her biri için 4 pekiştirme dersi ekler:
      Kelime Atölyesi, Grammar Lab, Reading & Listening, Speaking & Writing.
    - Sonuç: 6 seviye x 50 ders = 300 gerçek ders kaydı.
    """
    lessons = []

    def word_count_for(level):
        return 20 if level in ('A1', 'A2') else 50 if level in ('B1', 'B2') else 90

    def add_lesson(level, unit, position, title, grammar, vocab, example,
                   description=None, reading=None, listening=None,
                   speaking=None, writing=None):
        words = ', '.join(w for w, _ in vocab[:3])
        reading = reading or (
            f'{title} is the focus of this {level} lesson. '
            f'The learner practises {grammar}. Key language includes {words}. '
            f'Example: {example} The aim is to understand the message and use the target language in a real situation.'
        )
        listening = listening or (
            f'Listen carefully. Today we are studying {title}. {example} '
            f'Repeat the important words and notice how the sentence is connected in natural English.'
        )
        speaking = speaking or example
        writing = writing or (
            f'“{title}” konusu hakkında seviyene uygun en az {word_count_for(level)} kelimelik kısa bir İngilizce metin yaz.'
        )

        lessons.append({
            'level_code': level,
            'unit': unit,
            'position': position,
            'title': title,
            'description': description or f'{title}: {grammar} ve hedef kelimeler.',
            'grammar': grammar,
            'vocabulary': json.dumps([
                {'word': w, 'translation': tr, 'example': example}
                for w, tr in vocab
            ], ensure_ascii=False),
            'example': example,
            'reading_text': reading,
            'listening_text': listening,
            'speaking_prompt': speaking,
            'writing_prompt': writing,
            'quiz': make_quiz(title, grammar, vocab, example),
        })

    # Önce mevcut 10 ana dersi aynı position değerleriyle koru.
    for level, topics in TOPICS.items():
        for unit, (title, grammar, vocab, example) in enumerate(topics, start=1):
            add_lesson(
                level, unit, unit, title, grammar, vocab, example,
                description=f'Ünite {unit} ana dersi • {title}: {grammar} ve temel kullanım.'
            )

        # Ardından her ana üniteye 4 pekiştirme dersi ekle: 40 yeni ders.
        variants = [
            ('Kelime Atölyesi', 'vocabulary'),
            ('Grammar Lab', 'grammar'),
            ('Reading & Listening', 'receptive'),
            ('Speaking & Writing', 'productive'),
        ]

        next_position = 11
        for unit, (base_title, grammar, vocab, example) in enumerate(topics, start=1):
            words = ', '.join(w for w, _ in vocab)
            for suffix, kind in variants:
                title = f'{base_title} • {suffix}'

                if kind == 'vocabulary':
                    description = (
                        f'Ünite {unit} kelime pekiştirmesi • {base_title}. '
                        f'Hedef kelimeler: {words}.'
                    )
                    reading = (
                        f'Vocabulary workshop for {base_title}. Study the target words in context: {words}. '
                        f'Base example: {example} Notice meaning, spelling and natural word combinations.'
                    )
                    listening = (
                        f'Listen and repeat the target vocabulary for {base_title}: {words}. '
                        f'Then listen to the example sentence: {example}'
                    )
                    speaking = (
                        f'{base_title} konusunda hedef kelimelerden en az üçünü kullanarak '
                        f'{level} seviyesinde kısa İngilizce cümleler söyle. Örnek: {example}'
                    )
                    writing = (
                        f'{base_title} kelimelerinden en az dört tanesini kullanarak '
                        f'en az {word_count_for(level)} kelimelik bir İngilizce metin yaz.'
                    )

                elif kind == 'grammar':
                    description = (
                        f'Ünite {unit} grammar pekiştirmesi • {grammar}. '
                        f'Kuralı örnekler üzerinde uygula ve hata farkındalığı geliştir.'
                    )
                    reading = (
                        f'Grammar focus: {grammar}. Read the model carefully: {example} '
                        f'Identify the target structure and explain how it supports the meaning.'
                    )
                    listening = (
                        f'Listen for the grammar pattern {grammar}. Model sentence: {example} '
                        f'Focus on the words that signal the target structure.'
                    )
                    speaking = (
                        f'{grammar} yapısını kullanarak {base_title} hakkında en az üç İngilizce cümle kur.'
                    )
                    writing = (
                        f'{grammar} yapısını en az üç kez kullanarak {base_title} hakkında '
                        f'en az {word_count_for(level)} kelimelik bir metin yaz.'
                    )

                elif kind == 'receptive':
                    description = (
                        f'Ünite {unit} anlama çalışması • {base_title}. '
                        f'Okuma ve dinlemede ana fikir, ayrıntı ve hedef dili yakala.'
                    )
                    reading = (
                        f'Reading practice — {base_title}. {example} '
                        f'The text develops the theme using {grammar}. '
                        f'Look for the main idea, supporting details and the target vocabulary: {words}.'
                    )
                    listening = (
                        f'Listening practice — {base_title}. {example} '
                        f'Listen once for the main idea, then again for details and examples of {grammar}.'
                    )
                    speaking = (
                        f'Okuduğun ve dinlediğin {base_title} içeriğini İngilizce 2-4 cümleyle özetle.'
                    )
                    writing = (
                        f'{base_title} okuma/dinleme içeriğinin ana fikrini ve iki ayrıntısını '
                        f'en az {word_count_for(level)} kelimeyle İngilizce yaz.'
                    )

                else:  # productive
                    description = (
                        f'Ünite {unit} üretim çalışması • {base_title}. '
                        f'Konuşma ve yazmada {grammar} yapısını bağımsız kullan.'
                    )
                    reading = (
                        f'Production model — {base_title}. Read this model before producing your own response: {example} '
                        f'Use the model as guidance, but create original sentences.'
                    )
                    listening = (
                        f'Listen to the model response for {base_title}: {example} '
                        f'Then prepare your own response with similar clarity and correct use of {grammar}.'
                    )
                    speaking = (
                        f'{base_title} konusunda {grammar} yapısını kullanarak '
                        f'{30 if level in ("A1", "A2") else 60 if level in ("B1", "B2") else 90} saniyelik İngilizce konuşma hazırla.'
                    )
                    writing = (
                        f'{base_title} konusunda {grammar} yapısını ve hedef kelimeleri kullanarak '
                        f'en az {word_count_for(level)} kelimelik özgün bir İngilizce metin yaz.'
                    )

                add_lesson(
                    level, unit, next_position, title, grammar, vocab, example,
                    description=description,
                    reading=reading,
                    listening=listening,
                    speaking=speaking,
                    writing=writing,
                )
                next_position += 1

    return lessons


PLACEMENT_QUESTIONS = [
    ('A1', 'Hello ne demektir?', ['Merhaba','Hoşça kal','Gece','Kitap'], 0),
    ('A1', 'I ___ a student.', ['am','is','are','be'], 0),
    ('A1', 'Twenty hangi sayıdır?', ['2','12','20','200'], 2),
    ('A2', 'Yesterday I ___ to school.', ['go','went','gone','going'], 1),
    ('A2', 'You look tired. You ___ rest.', ['should','were','did','has'], 0),
    ('A2', 'This car is ___ than mine.', ['fast','faster','fastest','more fast'], 1),
    ('B1', 'If it rains, we ___ at home.', ['stay','stayed','will stay','would stayed'], 2),
    ('B1', 'I ___ English for three years.', ['study','studied','have studied','am study'], 2),
    ('B1', 'A doctor is someone ___ treats patients.', ['which','who','where','when'], 1),
    ('B2', 'She said that she ___ the task the next day.', ['finishes','would finish','will finishing','has finish'], 1),
    ('B2', 'If I had known, I ___ differently.', ['act','would have acted','will act','acted'], 1),
    ('B2', '“carry out” en yakın hangi anlama gelir?', ['iptal etmek','gerçekleştirmek','kaçmak','unutmak'], 1),
    ('C1', 'Which is the best hedge? “The results ___ indicate a trend.”', ['definitely prove','may','always','must certainly'], 1),
    ('C1', '“notwithstanding” en yakın hangi bağlaçtır?', ['because of','despite','therefore','unless'], 1),
    ('C1', 'A synthesis should primarily…', ['copy one source','integrate multiple sources','avoid comparison','use only quotations'], 1),
    ('C2', '“read between the lines” neyi ifade eder?', ['hızlı okumak','örtük anlamı çıkarmak','sesli okumak','satır numaralamak'], 1),
    ('C2', '“succinct” kelimesine en yakın anlam hangisidir?', ['gereksiz uzun','özlü','belirsiz','duygusal'], 1),
    ('C2', 'A literal interpretation may miss…', ['spelling','subtext and irony','word count','punctuation only'], 1),
]
