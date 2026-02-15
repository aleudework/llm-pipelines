from goldcode.utils.db_downloader import DBDownloader
import pandas as pd

sql = """


select
l.sel,
l.afd,
l.lejemaal,
concat(l.Adresse, ' ', l.Beliggenhed, ', ', l.PostBy) as Adresse,
aft.Tekst as 'Beskrivelse',
lmt.Tekst as 'Lejemålstype'
from Lejemaal l
left join Afdtekster aft on aft.sel = l.sel and aft.afd = l.afd and aft.Overskrift = 'Beskrivelsestekst' and aft.art = 'Afdelingsbeskrivelse'
left join LMtyper lmt on lmt.kode = l.Lmtype


"""

db = DBDownloader()
db.set_default_eg_prod()

df = db.sql(sql)

out = '/Users/alhu/Downloads/lejemålsetager_260214.xlsx'
df.to_excel(out, index=False)