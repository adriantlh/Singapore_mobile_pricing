import cloudscraper

def test_cloudscraper():
    scraper = cloudscraper.create_scraper()
    url = "https://mobyshop.com.sg/"
    print(f"Testing cloudscraper on {url}...")
    try:
        resp = scraper.get(url)
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"Success! Preview: {resp.text[:200]}")
        else:
            print(f"Failed with status: {resp.status_code}")
            print(f"Body preview: {resp.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_cloudscraper()
