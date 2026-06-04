import os, time, json, pickle, requests
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build







class Blogger:
    def __init__(self, file):
        self.file = file
        self.filesize = os.path.getsize(file)
        self.filename = file.split('/')[-1]
        self.accessToken = None
        self.imageUrls = {}
        self.creds = self._get_credentials()
        self.accessToken = self.creds.token
        self.session = requests.Session()

    def _get_credentials(self):
        """Load or refresh credentials from token.pickle."""
        creds = None
        try:
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        except FileNotFoundError:
            pass

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', ["https://www.googleapis.com/auth/blogger"]
                )
                creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return creds

    def refreshAccessToken(self):
        """Refresh token using the credentials object."""
        self.creds.refresh(Request())
        self.accessToken = self.creds.token

    def getUploadUrl(self, size):
        url = "https://docs.google.com/upload/blogger/photos/resumable"
        querystring = {"authuser": "0", "opi": "98421741"}
        payload = {
            "protocolVersion": "0.8",
            "createSessionRequest": {
                "fields": [
                    {"external": {"name": "file", "filename": f"{self.filename}", "put": {}, "size": size}},
                    {"inlined": {"name": "title", "content": f"{self.filename}", "contentType": "text/plain"}},
                    {"inlined": {"name": "addtime", "content": "1780504046292", "contentType": "text/plain"}},
                    {"inlined": {"name": "onepick_version", "content": "v2", "contentType": "text/plain"}},
                    {"inlined": {"name": "onepick_host_id", "content": "10", "contentType": "text/plain"}},
                    {"inlined": {"name": "onepick_host_usecase", "content": "RichEditor", "contentType": "text/plain"}},
                    {"inlined": {"name": "album_mode", "content": "permanent", "contentType": "text/plain"}},
                    {"inlined": {"name": "silo_id", "content": "3", "contentType": "text/plain"}},
                ]
            },
        }

        for i in range(30):
            headers = {
                "x-client-pctx": "CgcSBWjtl_cu",
                "x-goog-upload-command": "start",
                "x-goog-upload-header-content-length": f"{size}",
                "x-goog-upload-header-content-type": "image/png",
                "x-goog-upload-protocol": "resumable",
                "authorization": f"Bearer {self.accessToken}",
                "content-type": "application/x-www-form-urlencoded",
            }
            response = self.session.post(url, data=json.dumps(payload), headers=headers, params=querystring)
            if response.ok and "AUTH_REQUIRED" not in response.text:
                return response.headers["x-goog-upload-url"]
            else:
                print("Error:getUploadUrl", response.status_code, response.text, flush=True)
                self.refreshAccessToken()
                raise Exception()

    def upload(self):
        with open(self.file, "rb") as f:
            rawData = f.read()
            for i in range(30):
                try:
                    uploadUrl = self.getUploadUrl(len(rawData))
                    headers = {
                        "accept": "*/*",
                        "content-type": "image/png",
                        "origin": "https://docs.google.com",
                        "referer": "https://docs.google.com/",
                        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
                        "x-client-pctx": "CgcSBWjtl_cu",
                        "x-goog-upload-command": "upload, finalize",
                        "x-goog-upload-offset": "0",
                    }
                    response = self.session.post(uploadUrl, headers=headers, data=rawData)
                    if response.ok:
                        imageUrl = (
                            response.json()["sessionStatus"]["additionalInfo"]
                            ["uploader_service.GoogleRupioAdditionalInfo"]
                            ["completionInfo"]["customerSpecificInfo"]["url"]
                        )
                        components = imageUrl.split("/")
                        baseUrl = "/".join(components[:-1])
                        url = f"{baseUrl}/s0/{components[-1]}"
                        print(url)
                        return url
                    else:
                        print(f"Error:uploadChunk attempt {i}", response.status_code, response.text, flush=True)
                        self.refreshAccessToken()
                        raise Exception()
                except Exception as e:
                    print(e, flush=True)
                    time.sleep(1)


if __name__ == "__main__":
    uploader = Blogger("./legacy-icon.jpg")
    uploader.upload()
