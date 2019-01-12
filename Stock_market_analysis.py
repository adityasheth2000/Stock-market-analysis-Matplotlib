import fix_yahoo_finance as yf
import matplotlib.pyplot as plt
import datetime
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates
import pandas as pd

stock=raw_input("Stock name:")      #Name of Stock in Market(For example: AAPL for Apple,AMZN for Amazon)
startdate=raw_input("Start date:")  #input in the form yyyy-mm-dd
enddate=raw_input("End date:")    #input in the form yyyy-mm-dd


class Graph:
    def __init__(self,stockname,startdate,enddate): #to get information about the stockname,startdate,and enddate
        self.ticker=stockname
        self.start=startdate
        self.end=enddate

    def collect_data(self):#Collecting data from a module called fix_yahoo_finance which uses pandas_datareader to extract information from newly updated yahoo_finance
        self.data=yf.download(self.ticker,self.start,self.end)
        print self.data
    
    def useful_data(self): # function made to calculate all the useful information that will be later used to plot the graph
        

        self.date=[]
        self.close_val=[]
        self.growth=[]
        self.five_day_simple_moving_avg=[]
        self.twenty_day_simple_moving_avg=[]
        self.five_day_weighted_moving_avg=[]
        self.twenty_day_weighted_moving_avg=[]
        self.rsi=[]
        self.growth=[]
        self.volume=[]
        self.max_vol=0
        length=len(self.data)
        sum=0
        for i in self.data.index:
            self.date.append(str(i)[:10])
        self.data.reset_index(inplace=True)
        self.data['Date']=pd.to_datetime(self.data['Date'])
        self.data["Date"]=self.data["Date"].apply(mdates.date2num)
        self.ohlc=self.data[['Date','Open','High','Low','Close']].copy()

        for i in range(length):
            self.close_val.append(self.data['Adj Close'][i])
            self.volume.append(self.data.Volume[i])
            if(self.data.Volume[i]>self.max_vol):
                self.max_vol=self.data.Volume[i]
        for i in range(length):
            if(i<length-1):
                self.growth.append((self.close_val[i+1]-self.close_val[i])/self.close_val[i])
        
        cnt=0
        sum_weighted=0
        total_volume=0
        for i in range(length):
            sum=sum+self.close_val[i]
            sum_weighted=sum_weighted+self.close_val[i]*self.data.Volume[i]
            total_volume=total_volume+self.data.Volume[i]
            if(i>3):
                self.five_day_simple_moving_avg.append(sum/5.0)
                self.five_day_weighted_moving_avg.append(sum_weighted/(total_volume*1.0))
                sum=sum-self.close_val[cnt]
                sum_weighted=sum_weighted-self.close_val[cnt]*self.data.Volume[cnt]
                total_volume=total_volume-self.data.Volume[cnt]
                cnt=cnt+1
        
        cnt=0
        sum=0
        total_volume=0
        sum_weighted=0
        for i in range(length):
            sum=sum+self.close_val[i]
            sum_weighted=sum_weighted+self.close_val[i]*self.data.Volume[i]
            total_volume=total_volume+self.data.Volume[i]
            if(i>18):
                self.twenty_day_simple_moving_avg.append(sum/20.0)
                self.twenty_day_weighted_moving_avg.append(sum_weighted/(total_volume*1.0))
                sum=sum-self.close_val[cnt]
                sum_weighted-=self.close_val[cnt]*self.data.Volume[cnt]
                total_volume-=self.data.Volume[cnt]
                cnt=cnt+1
        
    def calculate_rsi(self):#calculation of relative strength index is done in this function
        length=len(self.data)
        self.gain=[0]
        self.loss=[0]
        for i in range(length):
            if(i>0):
                if(self.close_val[i]>self.close_val[i-1]):
                    self.gain.append(self.close_val[i]-self.close_val[i-1])
                    self.loss.append(0)
                else:
                    self.loss.append(self.close_val[i-1]-self.close_val[i])
                    self.gain.append(0)
        
        self.rs=[]
        sum_gain=0.0
        sum_loss=0.0
        avg_gain=0.0
        avg_loss=0.0
        for i in range(length):
            if(i<=12):
                sum_gain=sum_gain+self.gain[i]
                sum_loss=sum_loss+self.loss[i]
            elif(i==13):
                sum_gain=sum_gain+self.gain[i]
                sum_loss=sum_loss+self.loss[i]
                avg_gain=sum_gain/14.0
                avg_loss=sum_loss/14.0
                self.rs.append(avg_gain/avg_loss)
                self.rsi.append(100-100/(1+self.rs.pop()))
            else:
                avg_gain=(avg_gain*13+self.gain[i])/14.0
                avg_loss=(avg_loss*13+self.loss[i])/14.0
                self.rs.append(avg_gain/avg_loss)
                self.rsi.append(100-100/(1+self.rs.pop()))

                
    def calculate_MACD(self):
        self.ema26=[]
        self.ema12=[]
        self.ema9=[]
        cnt=0
        sum=0
        length=len(self.data)
        for i in range(length):
            multiplier=2.0/(26.0+1.0)
            if(i<26):
                sum+=self.close_val[i]
            if(i==25):
                self.ema26.append(sum/26.0)
            if(i>25):
                self.ema26.append((self.close_val[i]-self.ema26[cnt])*multiplier+self.ema26[cnt])
                cnt+=1
        cnt=0
        sum=0
        #length=len(self.data)
        for i in range(length):
            multiplier=2.0/(12.0+1.0)
            if(i<12):
                sum+=self.close_val[i]
            if(i==11):
                self.ema12.append(sum/12.0)
            if(i>11):
                self.ema12.append((self.close_val[i]-self.ema12[cnt])*multiplier+self.ema12[cnt])
                cnt+=1
        
        self.macd=[]
        cnt=26-12
        for i in range(len(self.ema26)):
            self.macd.append(self.ema26[i]-self.ema12[i+cnt])
        
        
        
        self.macd_histogram=[]
        cnt=0
        sum=0
        length=len(self.macd)
        for i in range(length):
            multiplier=2.0/(9.0+1.0)
            if(i<9):
                sum+=self.macd[i]
            if(i==8):
                self.ema9.append(sum/9.0)
            if(i>8):
                self.ema9.append((self.macd[i]-self.ema9[cnt])*multiplier+self.ema9[cnt])
                cnt+=1
        
        
        cnt=len(self.macd)-len(self.ema9)
        for i in range(len(self.ema9)):
            self.macd_histogram.append(self.macd[i+cnt]-self.ema9[i])
        
            

                               



    def make_list_for_xtick(self):
        if(len(self.date)<=10):
            return [[i for i in range(len(self.date))],[self.date[i] for i in range(len(self.date))]]
        k=int(len(self.date)/10)
        i=0
        l1=[]
        l2=[]
        length=len(self.date)
        while(i<length):
            l1.append(i)
            l2.append(self.date[i])
            i=i+k
        return [l1,l2]



    def plot_graph(self):
        #print self.data
        growth1=plt.figure(5)
        plt.plot(self.date[:-1],self.growth,label='growth')
        plt.xlabel('Date')
        plt.xticks(self.make_list_for_xtick()[0],self.make_list_for_xtick()[1])
        plt.ylabel('Growth value')
        plt.title('Growth of stock')
        growth1.show()
        

        volume1=plt.figure(4)
        plt.bar(self.date,self.volume)
        plt.xlabel('Date')
        plt.ylabel('Volume')
        plt.title('Volume of stock traded in a day')
        plt.xticks(self.make_list_for_xtick()[0],self.make_list_for_xtick()[1])
        volume1.show()

        macdgraph=plt.figure(3)
        plt.title('MACD technical indicator')
        cnt=len(self.date)-len(self.ema9)
        ax_bar=plt.bar(self.date[cnt:],self.macd_histogram)
        length=range(len(self.date[cnt:]))
        for i in length[1:]:
            if(self.macd_histogram[i]>0):
                if(self.macd_histogram[i]>self.macd_histogram[i-1]):
                    ax_bar[i].set_color('Green')
                else:
                    ax_bar[i].set_color('palegreen')
            else:
                if(self.macd_histogram[i]>self.macd_histogram[i-1]):
                    ax_bar[i].set_color('indianred')
                else:
                    ax_bar[i].set_color('Red')




        plt.xlabel('Date')
        plt.ylabel('MACD')
        plt.xticks(self.make_list_for_xtick()[0],self.make_list_for_xtick()[1])
        plt.plot(self.date[len(self.date)-len(self.ema9):],self.ema9,label='Signal line')
        plt.plot(self.date[len(self.date)-len(self.ema9):],self.macd[len(self.macd)-len(self.ema9):],label='MACD line')
        plt.legend()
        macdgraph.show()

        

        rsi_graph=plt.figure(2)
        plt.plot(self.date[13:],self.rsi,label='RSI value')  #add a horizontal line at 30(oversold) and 70(overbought) 
        oversold=[30 for i in self.date[13:]]
        overbought=[70 for i in self.date[13:]]
        plt.plot(self.date[13:],oversold,linestyle='--',color='red')
        plt.plot(self.date[13:],overbought,linestyle='--',color='red')
        plt.xlabel('Date')
        plt.xticks(self.make_list_for_xtick()[0],self.make_list_for_xtick()[1])
        plt.ylabel('RSI value')   
        plt.title('RSI technical indicator')
        plt.legend()
        rsi_graph.show()

        stock_price_with_simple_avg=plt.figure(1)
        ax1=plt.subplot2grid((8,1),(0,0),rowspan=5,colspan=1)
        plt.xlabel('Date')
        plt.ylabel('Stock value(in $)')
        plt.xticks(self.make_list_for_xtick()[0],self.make_list_for_xtick()[1])
        plt.title('Stock price of '+self.ticker)
        plt.plot(self.date,self.close_val,label='Stock price')
        plt.plot(self.date[4:],self.five_day_simple_moving_avg,label='5 day simple moving average')
        plt.plot(self.date[19:],self.twenty_day_simple_moving_avg,label='20 day simple moving average')
        plt.legend()

        ax2=plt.subplot2grid((8,1),(6,0),rowspan=1,colspan=1,sharex=ax1)
        ax2.bar(self.date,self.volume)
        plt.xticks(self.make_list_for_xtick()[0],self.make_list_for_xtick()[1])
        plt.ylabel('Volume')
        stock_price_with_simple_avg.show()

        stock_price_with_weighted_avg=plt.figure(0)
        ax1=plt.subplot2grid((8,1),(0,0),rowspan=5,colspan=1)
        plt.xlabel('Date')
        plt.ylabel('Stock value(in $)')
        plt.xticks(self.make_list_for_xtick()[0],self.make_list_for_xtick()[1])
        plt.title('Stock price of '+self.ticker)
        plt.plot(self.date,self.close_val,label='Stock price')
        plt.plot(self.date[4:],self.five_day_weighted_moving_avg,label='5 day weighted moving average')
        plt.plot(self.date[19:],self.twenty_day_weighted_moving_avg,label='20 day weighted moving average')
        plt.legend()

        ax2=plt.subplot2grid((8,1),(6,0),rowspan=1,colspan=1,sharex=ax1)
        ax2.bar(self.date,self.volume)
        plt.xticks(self.make_list_for_xtick()[0],self.make_list_for_xtick()[1])
        plt.ylabel('Volume')
        stock_price_with_weighted_avg.show()


        
        f1,ax=plt.subplots(figsize=(10,5))
        plt.title('Stock analysis')
        plt.xlabel('Date')
        plt.ylabel('Stock price')
        plt.plot(self.data['Date'][4:],self.five_day_simple_moving_avg,label='5 day simple moving average')
        plt.plot(self.data['Date'][19:],self.twenty_day_simple_moving_avg,label='20 day simple moving average')
        candlestick_ohlc(ax,self.ohlc.values,width=1,colorup='green',colordown='red')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.legend()
        plt.show()
        
        raw_input("Press Enter to terminate:")    

    

ob=Graph(stock,startdate,enddate)
ob.collect_data()
ob.useful_data()
ob.calculate_rsi()
ob.calculate_MACD()
ob.plot_graph()  
   
