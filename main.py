import pathlib, audible, httpx, os

# get download link(s) for book
def _get_download_link(auth, asin, codec="LC_128_44100_stereo"):
    # need at least v0.4.0dev
    if auth.adp_token is None:
        raise Exception("No adp token present. Can't get download link.")

    try:
        content_url = ("https://cde-ta-g7g.amazon.com/FionaCDEServiceEngine/"
                       "FSDownloadContent")
        params = {
            'type': 'AUDI',
            'currentTransportMethod': 'WIFI',
            'key': asin,
            'codec': codec
        }            
        r = httpx.get(
            url=content_url,
            params=params,
            allow_redirects=False,
            auth=auth
        )

        # prepare link
        # see https://github.com/mkb79/Audible/issues/3#issuecomment-518099852
        link = r.headers['Location']
        tld = auth.locale.domain
        new_link = link.replace("cds.audible.com", f"cds.audible.{tld}")
        return new_link
    except Exception as e:
        print(f"Error: {e}")
        return


def download_file(url):
    r = httpx.get(url)

    try:
        title = r.headers["Content-Disposition"].split("filename=")[1]
        filename = pathlib.Path.cwd() / "audiobooks" / title
    
        with open(filename, 'wb') as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
        print(f"File downloaded in {r.elapsed}")
        return filename
    except KeyError:
        return "Nothing downloaded"


if __name__ == "__main__":
    Auth_file = "Credentials"
    
    if(not os.path.exists(Auth_file)):
        auth = audible.LoginAuthenticator(
            input("Username: "),
            input("Password: "),
            locale="it")

        auth.to_file(
            filename=Auth_file,
            password="1234",
            encryption="bytes")

        
    auth = audible.FileAuthenticator(
            filename=Auth_file,
            password="1234",
        )
        

    client = audible.Client(auth)

    library = client.get("library", num_results=1000)
    asins = [book["asin"] for book in library["items"]]

    for asin in asins:
        dl_link = _get_download_link(auth, asin)

        if dl_link:
            print(f"download link now: {dl_link}")
            status = download_file(dl_link)
            print(f"downloaded file: {status}")