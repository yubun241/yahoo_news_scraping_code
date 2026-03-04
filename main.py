import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime

# ========== プロキシ設定 ==========
PROXY = {
    'http': 'http://xx.xxx.x.xx:xxxx',
    'https': 'http://xx.xxx.x.xx:xxxx'
}

# ========== ユーザーエージェント設定 ==========
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# ========== ヤフーニュース URL ==========
YAHOO_NEWS_URL = "https://news.yahoo.co.jp/"

# ========== プロキシ接続テスト ==========
def test_proxy_connection():
    """プロキシ接続が正常か確認"""
    
    try:
        print("🔌 プロキシ接続をテスト中...\n")
        
        response = requests.get(
            'http://httpbin.org/ip',
            proxies=PROXY,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ プロキシ接続成功！")
            print(f"   IPアドレス: {response.json().get('origin')}\n")
            return True
        else:
            print(f"❌ プロキシテスト失敗（ステータスコード: {response.status_code}）\n")
            return False
    
    except requests.exceptions.ProxyError as e:
        print(f"❌ プロキシエラー: {e}")
        print("   プロキシアドレスが正しいか確認してください\n")
        return False
    
    except requests.exceptions.Timeout:
        print("❌ タイムアウト: プロキシへの接続がタイムアウトしました\n")
        return False
    
    except Exception as e:
        print(f"❌ エラー: {e}\n")
        return False

# ========== スクレイピング実行（プロキシ使用） ==========
def scrape_yahoo_news():
    """ヤフーニュースのトップニュースをスクレイピング"""
    
    try:
        print("🔍 ヤフーニュースにアクセス中...\n")
        
        # ページを取得（プロキシ経由）
        response = requests.get(
            YAHOO_NEWS_URL,
            headers=HEADERS,
            proxies=PROXY,
            timeout=15
        )
        response.encoding = 'utf-8'
        response.raise_for_status()
        
        print(f"✅ ページ取得成功（ステータスコード: {response.status_code}）\n")
        
        # HTML をパース
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # ニュース記事を抽出
        articles = []
        
        # トップニュースを取得
        news_items = soup.find_all('a', href=True)
        
        for idx, item in enumerate(news_items[:30], 1):
            try:
                title = item.get_text(strip=True)
                link = item.get('href')
                
                # 不要なタイトルをフィルタ
                if title and len(title) > 5 and link and 'news.yahoo.co.jp' in link:
                    # 相対URLを絶対URLに変換
                    if link.startswith('/'):
                        link = 'https://news.yahoo.co.jp' + link
                    
                    articles.append({
                        'no': len(articles) + 1,
                        'title': title,
                        'link': link
                    })
                    
                    if len(articles) >= 20:
                        break
            
            except Exception as e:
                continue
        
        return articles
    
    except requests.exceptions.ProxyError as e:
        print(f"❌ プロキシエラー: {e}")
        print("   プロキシサーバーが正しく動作していません\n")
        return []
    
    except requests.exceptions.RequestException as e:
        print(f"❌ 接続エラー: {e}\n")
        return []

# ========== CSV保存 ==========
def save_to_csv(articles, filename="yahoo_news.csv"):
    """ニュース記事をCSVファイルに保存"""
    
    import csv
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['no', 'title', 'link'])
            writer.writeheader()
            writer.writerows(articles)
        
        print(f"✅ {filename} に保存しました\n")
    
    except Exception as e:
        print(f"❌ 保存エラー: {e}\n")

# ========== メイン処理 ==========
def main():
    print("="*60)
    print("📰 ヤフーニュース スクレイピングツール（プロキシ対応）")
    print("="*60 + "\n")
    
    # プロキシ接続テスト
    if not test_proxy_connection():
        print("⚠️  プロキシ接続に失敗しました。終了します。\n")
        return
    
    # ニュース一覧を取得
    articles = scrape_yahoo_news()
    
    if articles:
        print(f"✅ {len(articles)} 件のニュースを取得しました\n")
        
        # 結果表示
        for article in articles[:10]:
            print(f"【{article['no']}】 {article['title']}")
            print(f"    Link: {article['link']}\n")
        
        # CSV保存
        save_to_csv(articles)
    
    else:
        print("❌ ニュースを取得できませんでした")

if __name__ == "__main__":
    main()
