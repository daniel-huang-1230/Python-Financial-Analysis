from flask import Flask, render_template


app = Flask(__name__)


@app.route('/')
def home():
    return render_template("home.html")

@app.route('/plot')
def plot():
    from pandas_datareader import data
    import datetime
    from bokeh.plotting import figure, show, output_file
    from bokeh.embed import components
    from bokeh.resources import CDN
    # the start and end parameter should be in "datetime object" format
    s = datetime.datetime(2017, 7, 1)
    e = datetime.datetime(2018, 1, 10)
    df = data.DataReader(name="GOOG", data_source="yahoo", start=s, end=e)

    p = figure(x_axis_type="datetime", width=1000, height=300, responsive=True)
    p.title.text = "Candlestick Chart(Google Stock Prices)"

    # a function that determines whether the close price is higher than the open price
    def inc_dec(c, o):
        if c > o:
            value = "Rise"
        elif c < o:
            value = "Drop"
        else:
            value = "Tie"
        return value

    df["Status"] = [inc_dec(c, o) for c, o in zip(df.Close, df.Open)]  # list comprehension
    df["Mid"] = (df.Open + df.Close) / 2
    df["Height"] = abs(df.Open - df.Close)

    # we build two types of rectangles-- one where the close price is higher, another one where the close price is lower
    hours_12 = 12 * 60 * 60 * 1000  # convert the width, which is 12 hours, to miliseconds

    p.segment(df.index, df.High, df.index, df.Low, color="black")
    p.rect(df.index[df.Status == "Rise"], df.Mid[df.Status == "Rise"], hours_12, df.Height[df.Status == "Rise"],
           fill_color="red", line_color="black")

    p.rect(df.index[df.Status == "Drop"], df.Mid[df.Status == "Drop"], hours_12, df.Height[df.Status == "Drop"],
           fill_color="#228B22", line_color="black")

    # load the html elements and JS script that containing all data with "embed" library
    script1, div1, = components(p)

    # load the bokeh JS and CSS files with "resources" library
    cdn_js = CDN.js_files
    cdn_css = CDN.css_files
    return render_template("plot.html",
                           script1=script1,
                           div1 = div1,
                           cdn_css = cdn_css[0],
                           cdn_js = cdn_js[0])

@app.route('/about')
def about():
    return render_template("about.html")


if __name__ == "__main__":
    app.run(debug=True)