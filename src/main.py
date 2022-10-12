import datetime
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from src.rss import channel_gen_rss
from src.tg_api import TGApiChannel
from src.utils import RssBridgeType, RssFormat
from src.yt_api import YTApiChannel

app = FastAPI()


@app.get("/rss-feed/{username}", response_class=FileResponse)
async def get_feed(
    username: str,
    bridge_type: RssBridgeType = RssBridgeType.TG,
    format: Optional[RssFormat] = RssFormat.ATOM,
    count: Optional[int] = None,
    days: Optional[int] = None,
    with_enclosures: Optional[bool] = False,
):
    if bridge_type is RssBridgeType.TG:
        channel_class = TGApiChannel
    elif bridge_type is RssBridgeType.YT:
        channel_class = YTApiChannel
    else:
        raise HTTPException(status_code=404, detail="Unknown bridge_type")  # TODO 404?

    channel = channel_class(username)

    after_date = datetime.date.today() - datetime.timedelta(1) * days if days else None
    items = channel.fetch_items(entries_count=count, after_date=after_date)

    path = channel_gen_rss(
        channel=channel,
        items=items,
        rss_format=format,
        use_enclosures=with_enclosures,
    )

    print(f"Generated RSS file: {path}")

    return FileResponse(path=path, media_type="text/xml")


if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=8081)
