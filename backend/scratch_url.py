from sqlalchemy.engine.url import make_url

raw = "postgresql://user:pass@ep-cool-snowflake-123.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
url_obj = make_url(raw)

print("Driver:", url_obj.drivername)
print("Query:", url_obj.query)

query = dict(url_obj.query)
sslmode = query.pop("sslmode", None)
query.pop("channel_binding", None)

url_obj = url_obj.set(query=query)
url_obj = url_obj.set(drivername="postgresql+asyncpg")

print("Normalized:", str(url_obj))
print("SSL Mode:", sslmode)
