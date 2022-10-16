import matplotlib.pyplot as plt
from tkinter import *
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates
from pmaw import PushshiftAPI
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime
import yfinance as yf
import numpy as np
import re

# read crypto currency list
crypto_list = pd.read_csv("digital_currency_list.csv")
# create a list to display for users
item_names = [crypto_list['currency name'][i] + " (" + crypto_list['currency code'][i] + ")"for i in range(crypto_list.shape[0])]
crypto_tup_list = [(crypto_list['currency name'][i], crypto_list['currency code'][i]) for i in range(crypto_list.shape[0])]
# create crypto currency to search for the code
crypto_dict = dict(zip(item_names, crypto_tup_list))

# initialize dataframe to store market historical data
global trading
global gold
global snp
global oil
global ftse
global coin_name
coin_name = ""
trading = pd.DataFrame({})
gold = pd.DataFrame({})
snp = pd.DataFrame({})
oil = pd.DataFrame({})
ftse = pd.DataFrame({})


# function that generate the trend analysis text of market data
def get_change_status(start, end):
    percent_change = round((end - start)*100/start,2)
    if percent_change < 0:
        status = "has decreased by "
    else:
        status = "has increased by "
    return status,percent_change


# function that generate the summary of market data
def summary():
    content = "In the selected time frame: \n"
    # gold dataframe
    global gold
    # s&p 500 dataframe
    global snp
    # oil dataframe
    global oil
    # ftse dataframe
    global ftse
    # coin dataframe
    global trading
    global coin_name
    start = cb2.get()
    end = cb3.get()
    coin_empty = trading.empty
        
    if start == "":
        start_gold = gold['Date'].min()
        start_ftse = ftse['Date'].min()
        start_snp= snp['Date'].min()
        start_oil = oil['Date'].min()
        if not coin_empty:
            start_coin=trading['Date'].min()
    else:
        start_gold = mdates.date2num(datetime.datetime.strptime(start, "%m-%d-%Y"))
        start_gold = gold[gold['Date'] >= start_gold]['Date'].min()
        start_ftse = mdates.date2num(datetime.datetime.strptime(start, "%m-%d-%Y"))
        start_ftse = ftse[ftse['Date'] >= start_ftse]['Date'].min()
        start_snp = mdates.date2num(datetime.datetime.strptime(start, "%m-%d-%Y"))
        start_snp = snp[snp['Date'] >= start_snp]['Date'].min()
        start_oil = mdates.date2num(datetime.datetime.strptime(start, "%m-%d-%Y"))
        start_oil = oil[oil['Date'] >= start_oil]['Date'].min()
        if not coin_empty:
            start_coin = mdates.date2num(datetime.datetime.strptime(start, "%m-%d-%Y"))
            start_coin = trading[trading['Date'] >= start_coin]['Date'].min()
    if end == "":
        end_gold = gold['Date'].max()
        end_snp = snp['Date'].max()
        end_ftse = ftse['Date'].max()
        end_oil = oil['Date'].max()
        if not coin_empty:
            end_coin= trading['Date'].max()
        
    else:
        end_gold = mdates.date2num(datetime.datetime.strptime(end, "%m-%d-%Y"))
        end_gold= gold[gold['Date'] <= end_gold]['Date'].max()
        end_snp = mdates.date2num(datetime.datetime.strptime(end, "%m-%d-%Y"))
        end_snp= snp[snp['Date'] <= end_snp]['Date'].max()
        end_ftse = mdates.date2num(datetime.datetime.strptime(end, "%m-%d-%Y"))
        end_ftse= ftse[ftse['Date'] <= end_ftse]['Date'].max()
        end_oil = mdates.date2num(datetime.datetime.strptime(end, "%m-%d-%Y"))
        end_oil= oil[oil['Date'] <= end_oil]['Date'].max()
        if not coin_empty:
            end_coin = mdates.date2num(datetime.datetime.strptime(end, "%m-%d-%Y"))
            end_coin = trading[trading['Date'] <= end_coin]['Date'].max()
    # start values
    start_val_gold = round(float(gold[gold['Date'] == start_gold]['Open']), 2)
    start_val_ftse = round(float(ftse[ftse['Date'] == start_ftse]['Open']), 2)
    start_val_snp = round(float(snp[snp['Date'] == start_snp]['Open']), 2)
    start_val_oil = round(float(oil[oil['Date'] == start_oil]['Open']), 2)
    if not coin_empty:
        start_val_coin = round(float(trading[trading['Date'] == start_coin]['Open']), 2)
    # end valuews
    end_val_gold = round(float(gold[gold['Date'] == end_gold]['Close']), 2)
    end_val_ftse = round(float(ftse[ftse['Date'] == end_ftse]['Close']), 2)
    end_val_snp = round(float(snp[snp['Date'] == end_snp]['Close']), 2)
    end_val_oil = round(float(oil[oil['Date'] == end_oil]['Close']), 2)
    if not coin_empty:
        end_val_coin = round(float(trading[trading['Date'] == end_coin]['Close']), 2)
    
    gold_text = get_change_status(start_val_gold,end_val_gold)
    content += "Gold "+gold_text[0]+str(abs(gold_text[1]))+"% \n"
    ftse_text = get_change_status(start_val_ftse,end_val_ftse)
    content += "FTSE "+ftse_text[0]+str(abs(ftse_text[1]))+"% \n"
    snp_text = get_change_status(start_val_snp,end_val_snp)
    content += "S&P500 "+snp_text[0]+str(abs(snp_text[1]))+"% \n"
    oil_text = get_change_status(start_val_oil,end_val_oil)
    content += "Crude Oil "+oil_text[0]+str(abs(oil_text[1]))+"% \n\n"
    if not coin_empty:
        coin_text = get_change_status(start_val_coin,end_val_coin)
        content += coin_name+" "+coin_text[0]+str(abs(coin_text[1]))+"% \n\n"
    
        avg_mkt = round((ftse_text[1]+snp_text[1])/2,2)
        if(coin_text[1] - avg_mkt) < 5 and (coin_text[1] - avg_mkt) > -5:
            coin_performance="similar"
        elif(coin_text[1] - avg_mkt > 5):
            coin_performance = "STRONG in comparision "
        else:
            coin_performance="WEAK in comparision "
    
        content+=coin_name+" performace is "+coin_performance+"to global markets."
        
    # update summary to the textbox
    update_text(text4, content)


# function that initialize the market index data
def index_init():
    global snp
    global oil
    global ftse
    global gold
    # download data from yfinance api
    snp = yf.download(tickers="^GSPC", period='3y', interval='1d').reset_index()
    snp['Date'] = snp['Date'].map(lambda x: mdates.date2num(x))
    oil = yf.download(tickers="CL=F", period='3y', interval='1d').reset_index()
    oil['Date'] = oil['Date'].map(lambda x: mdates.date2num(x))
    ftse = yf.download(tickers="^FTSE", period='3y', interval='1d').reset_index()
    ftse['Date'] = ftse['Date'].map(lambda x: mdates.date2num(x))
    gold = yf.download(tickers="GC=F", period='3y', interval='1d').reset_index()
    gold['Date'] = gold['Date'].map(lambda x: mdates.date2num(x))
    # draw candle stick plot
    draw_plot(gold, canvas3, index_plot1, "Gold")
    draw_plot(snp, canvas5, index_plot2, "S&P 500")
    draw_plot(oil, canvas6, index_plot3, "Crude Oil")
    draw_plot(ftse, canvas7, index_plot4, "FTSE")
    summary()


# return a sentiment score list for comments
def analyse_sentiment(comments):
    sentiment_analyzer = SentimentIntensityAnalyzer()
    compound = np.zeros(len(comments))
    for i in range(len(comments)):
        sentiment_dict = sentiment_analyzer.polarity_scores(comments.body[i])
        score = sentiment_dict["compound"]
        compound[i] = score
    return compound


#  function that get reddit comment and display
def get_reddit_comments(subreddit, limit, no_of_days):
    api = PushshiftAPI()
    before = int(datetime.datetime.now().timestamp())
    after = before - (no_of_days*86400)
    comments = api.search_comments(subreddit=subreddit, limit=limit, sort_type="score", sort="desc", before=before,after=after)
    print(f'Retrieved {len(comments)} comments from Pushshift')
    f_plot2.clear()
    f_plot2.tick_params(axis="x", labelsize=5)
    f_plot2.tick_params(axis="y", labelsize=5)
    if len(comments) != 0:
        if len(comments) >= 1000:
            num = "1K+"
        else:
            num = str(len(comments))
        comments_df = pd.DataFrame(comments)
        comments_df.sort_values(by=["score"], inplace=True, ascending=False)
        compound = analyse_sentiment(comments_df)
        content = "Total number of comments in that subreddit within a month: "+\
                  num + "\n\n" +\
                  "Comments with highest scores within a week:\n"
        if comments_df.shape[0] >= 5:
            for i in range(0, 5):
                content = content + "\n"+ str(i+1) + ". \n" + comments_df['body'][i] + "\n"
        else:
            for i in range(0, comments_df.shape[0]):
                content = content + "\n"+ str(i+1) + ". \n" + comments_df['body'][i] + "\n"
        update_text(text3, content)
        f_plot2.bar(["Positive", "Negative", "Neutral"],
                    [np.sum(compound > 0), np.sum(compound < 0), list(compound).count(0.0)])
        f_plot2.set_title("Number of Comments")

        canvas2.draw()

        f_plot2_2.bar(["Positive Score", "Negative Score"],
                      [compound[np.where(compound > 0)].sum(),
                       -compound[np.where(compound < 0)].sum()], color=["green", "red"])
        f_plot2_2.set_title("Positive vs Negative Totals")

        canvas2_2.draw()
    else:
        update_text(text3, "No comment in that subreddit within a month")
        canvas2_2.draw()


def removetag(text):
    pattern = re.compile('<.*?>')
    res = re.sub(pattern, '', text)
    return res


def scankey(event):
    val = event.widget.get()

    if val == '':
        data = item_names
    else:
        data = []
        for item in item_names:
            if val.lower() in item.lower():
                data.append(item)
    update(data)


# update content that showed in the listbox
def update(data):
    listbox.delete(0, 'end')

    # put new data
    for item in data:
        listbox.insert('end', item)


def update_text(text, data):
    char_list = [data[j] for j in range(len(data)) if ord(data[j]) in range(65536)]
    data = ''
    for j in char_list:
        data = data + j
    text.configure(state='normal')
    text.delete(1.0, 'end')
    text.insert('end', data)
    text.configure(state='disabled')


# refresh the coin plot after change the filter option
def update_coin_plot(code):
    global trading
    f_plot1.clear()
    url = 'https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol=' \
          + code \
          + '&market=USD&apikey=SX9BMX25514A9T67'
    r = requests.get(url)
    data = r.json()
    if "Error Message" in data.keys():
        trading = yf.download(tickers=code + '-USD', period='3y', interval='1d')
        trading = trading.reset_index()
        if trading.shape[0] == 0:
            f_plot1.set_title("No data found")
            canvas1.draw()
            plt.gca()
            canvas4.draw()
            return
        else:
            trading = trading.sort_values('Date', ascending=False)
    else:
        trading = pd.DataFrame.from_dict(data['Time Series (Digital Currency Daily)']).T.drop(['1b. open (USD)',
                                                                                               '2b. high (USD)',
                                                                                               '3b. low (USD)',
                                                                                               '4b. close (USD)',
                                                                                               '6. market cap (USD)'],
                                                                                              axis=1)
        trading = trading.reset_index()
        trading.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        trading['Date'] = pd.to_datetime(trading['Date'])
        trading['Open'] = trading['Open'].astype('float')
        trading['High'] = trading['High'].astype('float')
        trading['Low'] = trading['Low'].astype('float')
        trading['Close'] = trading['Close'].astype('float')
        trading['Volume'] = trading['Volume'].astype('float')
    cb2['values'] = trading['Date'].map(lambda x: x.strftime("%m-%d-%Y")).tolist()
    cb3['values'] = trading['Date'].map(lambda x: x.strftime("%m-%d-%Y")).tolist()
    cb6['values'] = trading['Date'].map(lambda x: x.strftime("%m-%d-%Y")).tolist()
    cb7['values'] = trading['Date'].map(lambda x: x.strftime("%m-%d-%Y")).tolist()
    choiceVar2.set(trading['Date'].min().strftime("%m-%d-%Y"))
    choiceVar3.set(trading['Date'].max().strftime("%m-%d-%Y"))
    trading['Date'] = trading['Date'].map(lambda x: mdates.date2num(x))
    f_plot1.xaxis_date()
    f_plot1.tick_params(axis="x", labelsize=5)
    f_plot1.tick_params(axis="y", labelsize=5)
    candlestick_ohlc(f_plot1,
                     trading.values,
                     width=0.6, colorup='g', colordown='r')
    canvas1.draw()
    plt.gca()
    canvas4.draw()


def selected_start_date(event):
    draw_coin_plot()
    draw_plot(gold, canvas3, index_plot1, "Gold")
    draw_plot(snp, canvas5, index_plot2, "S&P 500")
    draw_plot(oil, canvas6, index_plot3, "Crude Oil")
    draw_plot(ftse, canvas7, index_plot4, "FTSE")
    dt1 = cb2.get()
    tempDate = trading['Date'].map(lambda x: datetime.datetime.strftime(mdates.num2date(x), "%m-%d-%Y"))
    temp = (tempDate[
        tempDate.map(lambda x: datetime.datetime.strptime(x, "%m-%d-%Y")) >
        datetime.datetime.strptime(dt1, "%m-%d-%Y")]).tolist()
    cb3['values'] = temp
    cb7['values'] = temp
    summary()


def selected_end_date(event):
    draw_coin_plot()
    draw_plot(gold, canvas3, index_plot1, "Gold")
    draw_plot(snp, canvas5, index_plot2, "S&P 500")
    draw_plot(oil, canvas6, index_plot3, "Crude oil")
    draw_plot(ftse, canvas7, index_plot4, "FTSE")
    dt2 = cb3.get()
    tempDate = trading['Date'].map(lambda x: datetime.datetime.strftime(mdates.num2date(x), "%m-%d-%Y"))
    temp = (tempDate[
        tempDate.map(lambda x: datetime.datetime.strptime(x, "%m-%d-%Y")) <
        datetime.datetime.strptime(dt2, "%m-%d-%Y")]).tolist()
    cb2['values'] = temp
    cb6['values'] = temp
    summary()


def selected_freq(event):
    draw_coin_plot()
    draw_plot(gold, canvas3, index_plot1, "Gold")
    draw_plot(snp, canvas5, index_plot2,"S&P 500")
    draw_plot(oil, canvas6, index_plot3, "Crude Oil")
    draw_plot(ftse, canvas7, index_plot4, "FTSE")


def draw_coin_plot():
    global trading
    freq_dict = {'Yearly': '1Y', 'Monthly': '1M', 'Weekly': '1W-MON'}
    freq = cb1.get()
    dt1 = cb2.get()
    dt2 = cb3.get()
    f_plot1.clear()
    f_plot1.xaxis_date()
    if dt1 == "" and dt2 == "":
        return
    df = trading.copy()
    if freq != 'Daily':
        df['Date'] = df['Date'].map(lambda x: mdates.num2date(x))
        df = df.set_index('Date')
        df = df.resample(freq_dict[freq]).agg({'Open': 'first',
                                               'High': 'max',
                                               'Low': 'min',
                                               'Close': 'last',
                                               'Volume': 'sum'
                                               }).reset_index()
        df['Date'] = df['Date'].map(lambda x: mdates.date2num(x))
    if dt1 == "":
        candlestick_ohlc(f_plot1,
                         df[
                             df['Date'] < mdates.date2num(datetime.datetime.strptime(dt2, "%m-%d-%Y"))].values,
                         width=0.6, colorup='g', colordown='r')
    elif dt2 == "":
        candlestick_ohlc(f_plot1,
                         df[
                             df['Date'] > mdates.date2num(datetime.datetime.strptime(dt1, "%m-%d-%Y"))].values,
                         width=0.6, colorup='g', colordown='r')
    else:
        candlestick_ohlc(f_plot1,
                         df[
                             (df['Date'] > mdates.date2num(datetime.datetime.strptime(dt1, "%m-%d-%Y"))) &
                             (df['Date'] < mdates.date2num(datetime.datetime.strptime(dt2, "%m-%d-%Y")))].values,
                         width=0.6, colorup='g', colordown='r')
    canvas1.draw()
    plt.gca()
    canvas4.draw()


def selected_item():
    # Traverse the tuple returned by
    # curselection method and print
    # corresponding value(s) in the listbox
    for i in listbox.curselection():
        if listbox.get(i) == currentVar:
            return
        crypto_id = crypto_dict[listbox.get(i)][1] + '-' + crypto_dict[listbox.get(i)][0]
        print(crypto_id)
        url = "https://coinpaprika.com/coin/" + crypto_id + "/"
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')
        profile = soup.find_all("p", {"class": "cp-content-intro"})
        profile = [i.get_text() for i in profile]
        if len(profile) == 0:
            update_text(text1, "The cryptocurrency does not have a profile yet.")
        else:
            update_text(text1, profile[0])
        url = "https://data.messari.io/api/v1/news/" + crypto_dict[listbox.get(i)][1]
        r = requests.get(url)
        data = r.json()
        text = ""
        if 'data' not in data.keys():
            text = "No news related to this cryptocurrency."
        elif data['data'] is not None:
            for j in range(min(5, len(data['data']))):
                text = text + data['data'][j]['title'] + "\n" \
                       + data['data'][j]['author']['name'] + "\n" \
                       + data['data'][j]['content'] + "\n"
        else:
            text = "No news related to this cryptocurrency."
        
        update_text(text2, removetag(text))
        update_coin_plot(crypto_dict[listbox.get(i)][1])
        choiceVar1.set(choices1[0])
        draw_plot(gold, canvas3, index_plot1, "Gold")
        draw_plot(snp, canvas5, index_plot2, "S&P 500")
        draw_plot(oil, canvas6, index_plot3, "Crude Oil")
        draw_plot(ftse, canvas7, index_plot4, "FTSE")
        get_reddit_comments(crypto_dict[listbox.get(i)][0].lower(), 1200, 30)
        currentVar.set(listbox.get(i))
        global coin_name
        coin_name=crypto_dict[listbox.get(i)][0]
        summary()


def draw_plot(odf, cv, ax, title):
    df = odf.copy()
    df = df[['Date', 'Open', 'High', 'Low', 'Close']]
    ax.clear()
    freq_dict = {'Yearly': '1Y', 'Monthly': '1M', 'Weekly': '1W-MON'}
    freq = cb1.get()
    dt1 = cb2.get()
    dt2 = cb3.get()
    ax.xaxis_date()
    ax.tick_params(axis="x", labelsize=5)
    ax.tick_params(axis="y", labelsize=5)
    ax.set_title(title)
    if freq != 'Daily':
        df['Date'] = df['Date'].map(lambda x: mdates.num2date(x))
        df = df.set_index('Date')
        df = df.resample(freq_dict[freq]).agg({'Open': 'first',
                                               'High': 'max',
                                               'Low': 'min',
                                               'Close': 'last'
                                               }).reset_index()
        df['Date'] = df['Date'].map(lambda x: mdates.date2num(x))
    if dt1 == "" and dt2 == "":
        candlestick_ohlc(ax,
                         df.values,
                         width=0.6, colorup='g', colordown='r')
    elif dt1 == "":
        candlestick_ohlc(ax,
                         df[
                             df['Date'] < mdates.date2num(datetime.datetime.strptime(dt2, "%m-%d-%Y"))].values,
                         width=0.6, colorup='g', colordown='r')
    elif dt2 == "":
        candlestick_ohlc(ax,
                         df[
                             df['Date'] > mdates.date2num(datetime.datetime.strptime(dt1, "%m-%d-%Y"))].values,
                         width=0.6, colorup='g', colordown='r')
    else:
        candlestick_ohlc(ax,
                         df[
                             (df['Date'] > mdates.date2num(datetime.datetime.strptime(dt1, "%m-%d-%Y"))) &
                             (df['Date'] < mdates.date2num(datetime.datetime.strptime(dt2, "%m-%d-%Y")))].values,
                         width=0.6, colorup='g', colordown='r')
    cv.draw()


def quit():
    root.destroy()


if __name__ == '__main__':
    root = Tk()
    photo = PhotoImage(file="icon.png")  # load icon
    root.iconphoto(False, photo)
    root.title('Decrypto')

    root.geometry('1600x1000')  # set the size of frame

    tab_main = ttk.Notebook()
    tab_main.pack(pady=0, expand=True)
    tab1 = ttk.Frame(tab_main, width=1600, height=800)
    tab2 = ttk.Frame(tab_main, width=1600, height=800)
    tab3 = ttk.Frame(tab_main, width=1600, height=800)
    tab1.pack(pady=30, expand=True)
    tab2.pack(pady=30, expand=True)
    tab3.pack(pady=30, expand=True)

    # first page
    tab1.place(x=0, y=30)
    tab_main.add(tab1, text='Coin Information')

    Label(tab1, text='Enter coin name', width=20).place(x=-20, y=10)
    currentVar = StringVar()

    entry = Entry(tab1, width=20)
    entry.place(x=10, y=30)
    entry.bind('<KeyRelease>', scankey)

    listbox = Listbox(tab1, height=28)
    listbox.place(x=10, y=60)
    update(item_names)

    button = Button(tab1, text='Search', width=16, command=selected_item)
    button.place(x=10, y=530)

    label1 = Label(tab1, text='Profile')
    label1.place(x=200, y=40)
    text1 = Text(tab1, state='disabled', height=15, width=65, wrap=WORD)
    text1.place(x=200, y=60)

    label2 = Label(tab1, text='News')
    label2.place(x=200, y=320)
    text2 = Text(tab1, state='disabled', height=20, width=65, wrap=WORD)
    text2.place(x=200, y=340)

    label3 = Label(tab1, text='Price Chart')
    label3.place(x=800, y=40)
    fig1 = plt.figure(figsize=(6,4.5), dpi=110)
    f_plot1 =fig1.add_subplot(111)
    canvas1 = FigureCanvasTkAgg(fig1, tab1)
    canvas1.get_tk_widget().place(x=800, y=60)
    label4 = Label(tab1, text='Frequency: ', width=9)
    label4.place(x=800, y=600)
    choiceVar1 = StringVar()
    choices1 = ["Daily", "Weekly", "Monthly", "Yearly"]
    choiceVar1.set(choices1[0])
    cb1 = ttk.Combobox(tab1, textvariable=choiceVar1, state="readonly", values=choices1, width=10)
    cb1.place(x=895, y=600)
    cb1.bind("<<ComboboxSelected>>", selected_freq)
    label5 = Label(tab1, text='Start Date: ', width=9)
    label5.place(x=800, y=570)
    choiceVar2 = StringVar()
    choices2 = []
    cb2 = ttk.Combobox(tab1, textvariable=choiceVar2, state="readonly", values=choices2, width=10)
    cb2.place(x=895, y=570)
    cb2.bind("<<ComboboxSelected>>", selected_start_date)
    label6 = Label(tab1, text='End Date: ')
    label6.place(x=1110, y=570)
    choiceVar3 = StringVar()
    choices3 = []
    cb3 = ttk.Combobox(tab1, textvariable=choiceVar3, state="readonly", values=choices3, width=10)
    cb3.bind("<<ComboboxSelected>>", selected_end_date)
    cb3.place(x=1190, y=570)

    # second page
    tab2.place(x=100, y=30)
    tab_main.add(tab2, text='Public Sentiment Analysis')
    text3 = Text(tab2, state='disabled', height=15, width=90, wrap=WORD)
    text3.place(x=400, y=470) #sentiment analysis text box
    fig2 = plt.figure(figsize=(3.5, 4), dpi=100)
    f_plot2 = fig2.add_subplot(111)
    canvas2 = FigureCanvasTkAgg(fig2, tab2)
    canvas2.get_tk_widget().place(x=800, y=30) #sentiment analysis chart2

    fig2_2 = plt.figure(figsize=(3.5, 4), dpi=100)
    f_plot2_2 = fig2_2.add_subplot(111)
    canvas2_2 = FigureCanvasTkAgg(fig2_2, tab2)
    canvas2_2.get_tk_widget().place(x=380, y=30) #sentiment analysis chart1

    # third page
    tab3.place(x=100, y=30)
    tab_main.add(tab3, text='Price Comparision')
    label3 = Label(tab3, text='Global Indices & Indicators')
    label3.place(x=720, y=10)
    fig3 = plt.figure(figsize=(3.9, 2.8), dpi=100)
    index_plot1 = fig3.add_subplot(111)
    canvas3 = FigureCanvasTkAgg(fig3, tab3)
    canvas3.get_tk_widget().place(x=1100, y=350) #gold
    index_plot1.xaxis_date()
    canvas3.draw()

    label7 = Label(tab3, text='Frequency')
    label7.place(x=10, y=517)

    cb5 = ttk.Combobox(tab3, textvariable=choiceVar1, state="readonly", values=choices1, width=10)
    cb5.place(x=80, y=517)
    cb5.bind("<<ComboboxSelected>>", selected_freq)

    label8 = Label(tab3, text='Start Date')
    label8.place(x=180, y=517)

    choices6 = []
    cb6 = ttk.Combobox(tab3, textvariable=choiceVar2, state="readonly", values=choices6, width=10)
    cb6.place(x=250, y=517)
    cb6.bind("<<ComboboxSelected>>", selected_start_date)

    label9 = Label(tab3, text='End Date')
    label9.place(x=350, y=517)

    choices7 = []
    cb7 = ttk.Combobox(tab3, textvariable=choiceVar3, state="readonly", values=choices7, width=10)
    cb7.bind("<<ComboboxSelected>>", selected_end_date)
    cb7.place(x=415, y=517)

    fig5 = plt.figure(figsize=(3.9, 2.8), dpi=100)
    index_plot2 = fig5.add_subplot(111)
    canvas5 = FigureCanvasTkAgg(fig5, tab3)
    canvas5.get_tk_widget().place(x=720, y=70)  # s&p
    index_plot2.xaxis_date()
    canvas5.draw()

    fig6 = plt.figure(figsize=(3.9, 2.8), dpi=100)
    index_plot3 = fig6.add_subplot(111)
    canvas6 = FigureCanvasTkAgg(fig6, tab3)
    canvas6.get_tk_widget().place(x=720, y=350)  # crude oil
    index_plot3.xaxis_date()
    canvas6.draw()

    fig7 = plt.figure(figsize=(3.9, 2.8), dpi=100)
    index_plot4 = fig7.add_subplot(111)
    canvas7 = FigureCanvasTkAgg(fig7, tab3)
    canvas7.get_tk_widget().place(x=1100, y=70) # ftse
    index_plot4.xaxis_date()
    canvas7.draw()

    text4 = Text(tab3, state='disabled', height=9, width=82, wrap=WORD)
    text4.place(x=10, y=550)  # summary

    index_init()

    canvas4 = FigureCanvasTkAgg(fig1, tab3)
    canvas4.get_tk_widget().place(x=10, y=10)
    index_plot1.xaxis_date()
    canvas4.draw()

    root.mainloop()
