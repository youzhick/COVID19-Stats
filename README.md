# COVID19-Stats
Statistics builder and drawer for COVID-19 pandemy. <br>
See [stats.ipynb](./stats.ipynb) how the endpoint usage feels and looks.

# Data sources
Per-day data is taken from [2019 Novel Coronavirus COVID-19 (2019-nCoV) Data Repository by Johns Hopkins CSSE](https://github.com/CSSEGISandData/COVID-19) repository which is added as a submodule (don't forget to init&update after clone).<br>

Countries population data is taken from [Worldmeters.info](https://www.worldometers.info/world-population/population-by-country/). The html file will be requested and saved automatically. Be sure to stay online on the first <b>loadAll()</b> run.
