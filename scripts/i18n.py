"""Japanese translations of the website's interface (menus, labels, buttons, page texts).

Articles themselves are translated separately (content/posts-ja/). Any English text not listed
here simply stays in English, so the site never breaks if a new label is added later.
"""

JA = {
    # header and footer
    "Skip to content": "本文へスキップ",
    "Cybersecurity news, articles, training &amp; courses": "サイバーセキュリティのニュース・記事・トレーニング・コース",
    "Subscribe": "購読する",
    "Search ZNexora Tech": "ZNexora Tech を検索",
    "Search news, CVEs, topics": "ニュース・CVE・トピックを検索",
    "Switch light or dark theme": "ライト／ダークテーマを切り替え",
    "Sections": "セクション",
    "Follow us": "フォロー",
    "RSS feed": "RSS フィード",
    "Company": "ZNexora Tech",
    "Privacy": "プライバシー",
    "All articles": "すべての投稿",
    "Home": "ホーム",
    "Blog": "ブログ",
    "About": "概要",
    "Content summarises public sources. Always confirm details with the vendor or original report.":
        "本サイトの内容は公開情報をもとにまとめたものです。詳細は必ずベンダーや元の報道でご確認ください。",
    # building blocks
    "On our blog": "ブログ記事",
    "See all": "すべて見る",
    "Exploited right now": "現在悪用されている脆弱性",
    "All exploited vulnerabilities →": "悪用されている脆弱性をすべて見る →",
    "Weekly recap": "週間まとめ",
    "Read this week’s recap →": "今週のまとめを読む →",
    "Follow ZNexora Tech": "ZNexora Tech をフォロー",
    "About ZNexora Tech": "ZNexora Tech について",
    "Learn more →": "詳しく見る →",
    "Never miss an update": "最新情報を見逃さない",
    "Get new articles as soon as they are published.": "新しい記事が公開されたら、すぐにお届けします。",
    # home
    "Latest": "最新",
    "New stories appear here once approved.": "承認された記事がここに表示されます。",
    "Learn: articles, training & courses": "学ぶ：記事・トレーニング・コース",
    "From the ZNexora Blog": "ZNexora ブログより",
    "More from the blog": "ブログをもっと見る",
    "Join the ZNexora community": "ZNexora コミュニティに参加しよう",
    "Daily security news, tips and guides on your favourite platform.": "毎日のセキュリティニュース、ヒント、ガイドを、お好きなプラットフォームで。",
    "Latest cybersecurity news": "最新のサイバーセキュリティニュース",
    "The latest stories appear here once they are approved.": "承認された最新記事がここに表示されます。",
    # article page
    "CVE": "CVE",
    "Vendor": "ベンダー",
    "Product": "製品",
    "CVSS score": "CVSS スコア",
    "Severity": "深刻度",
    "Ransomware use": "ランサムウェアでの悪用",
    "Reported by CISA": "CISA が報告",
    "Level": "レベル",
    "Original report": "元の報道",
    "source": "出典",
    "Key points": "要点",
    "Share on": "共有：",
    "On this page": "このページの内容",
    "Related content": "関連コンテンツ",
    "Thank you for reading!": "最後までお読みいただき、ありがとうございます！",
    "Let’s continue to build a safer and more trustworthy digital future together.":
        "より安全で信頼できるデジタルの未来を、一緒に築いていきましょう。",
    "By": "執筆：",
    "min read": "分で読めます",
    "Share this article": "この記事を共有",
    "Share": "共有",
    # lists
    "Section": "セクション",
    "Articles appear here once they are approved.": "承認された記事がここに表示されます。",
    "Everything published on ZNexora Tech, newest first.": "ZNexora Tech で公開したすべての投稿（新しい順）。",
    "In-depth articles, hands-on training and structured courses for defenders.":
        "詳しい記事、実践的なトレーニング、体系的なコースで、防御の力を高めましょう。",
    # blog page
    "The ZNexora Blog": "ZNexora ブログ",
    "In-depth guides, awareness articles and security insights from our team.": "私たちのチームによる詳しいガイド、啓発記事、セキュリティの知見。",
    "Visit the full blog": "ブログを見る",
    "Our latest blog posts will appear here shortly.": "最新のブログ記事がまもなくここに表示されます。",
    "In-depth guides and security insights from the ZNexora Tech blog.": "ZNexora Tech ブログの詳しいガイドとセキュリティの知見。",
    # language
    "English": "英語",
}

JA_CATEGORIES = {
    "news": "最新ニュース",
    "weekly-recap": "週間まとめ",
    "exploited-vulnerabilities": "悪用されている脆弱性",
    "theory": "記事",
    "practical": "トレーニング",
    "courses": "コース",
    "cheatsheets": "チートシート",
}

JA_CAT_INTRO = {
    "news": "知っておくべきセキュリティニュースを、わかりやすく解説します。",
    "weekly-recap": "毎週月曜日：今週の主要ニュース、ランサムウェアの動向、Web 改ざんをまとめてお届けします。",
    "exploited-vulnerabilities": "いま攻撃者に悪用されている脆弱性と、優先して適用すべき対策。",
    "theory": "セキュリティの概念、脅威、テクノロジーを基礎から応用まで掘り下げる記事。",
    "practical": "実際のシステムを守るための、ステップごとの実践トレーニング。",
    "courses": "基礎から実践まで、モジュールごとに着実に学べる体系的なコース。",
    "cheatsheets": "ダウンロード、印刷、共有できる 1 ページのリファレンス集。",
}

JA_SEVERITY = {"critical": "緊急", "high": "重要", "medium": "警告", "low": "注意", "unscored": "未評価"}

JA_SITE = {
    "tagline": "未来を、安全に切り拓く。",
    "description": "サイバーセキュリティのニュース、週間の脅威まとめ、記事、トレーニング、コースで、組織が安全に未来へ進むためのお手伝いをします。",
    "mission": "ZNexora Tech は、イノベーション、卓越したサイバーセキュリティ、デジタルトランスフォーメーション、そして先進的なテクノロジーソリューションを通じて、組織が安全に未来を切り拓くことを支援します。",
}

JA_WEEKDAYS = "月火水木金土日"
