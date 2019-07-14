# coding: utf-8

from tk_library import excel_to_df
import matplotlib.pyplot as plt

from plotly.offline import iplot, init_notebook_mode
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.io as pio
from pyod.models.knn import KNN
from tk_library import combine_regexes

import os 
import glob
import datetime
from multiprocessing import Process
from fpdf import FPDF
from PIL import Image
import numpy as np
import seaborn as sns

class Analysis(object):

    def __init__(self,file_name,outlier):

        _, self.nvda_PL, self.nvda_BS, self.nvda_CF = excel_to_df("NVDA_Q.xls")
        del(self.nvda_BS["Assets"])
        self.nvda_BS.columns = list(map(self.lower,self.nvda_BS.columns.tolist()))
        init_notebook_mode(connected=True)
        if not outlier:
            if os.path.exists(r"C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\result"):
                os.mkdir(os.path.join(r"C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\result",datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
                self.path = os.path.join(r"C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\result",\
                                         os.listdir(r"C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\result")[-1])
                
            else:
                os.mkdir(r"C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\result")
                os.mkdir(os.path.join(r"C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\result",datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')))
                self.path = os.path.join(r"C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\result",\
                                         os.listdir(r"C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\result")[-1])
        else:
            pass
        
    def preprocess(self):
        
        try:
            self.nvda_BS["_total current assets"] = self.nvda_BS["cash and cash equivalents"] + self.nvda_BS["marketable securities"] \
                                                    + self.nvda_BS["accounts receivable, net"] + self.nvda_BS["inventories"] + \
                                                    self.nvda_BS["prepaid expenses and other current assets"]+ self.nvda_BS["deferred income taxes"]
        except:
            pass

        try:
            self.nvda_BS["_noncurrent assets"] = self.nvda_BS["property and equipment, net"] + self.nvda_BS["goodwill"] +\
                                                 self.nvda_BS["intangible assets, net"] + self.nvda_BS["other assets"]
        except:
            pass

        try:
            self.nvda_BS["_total assets"] = self.nvda_BS["_noncurrent assets"] + self.nvda_BS["_total current assets"] 
        except:
            self.nvda_BS["_total assets"] = self.nvda_BS["total noncurrent assets"] + self.nvda_BS["total current assets"]

        try:
            self.nvda_BS["_total liabilities"] = self.nvda_BS["accounts payable"] + self.nvda_BS["accrued and other current liabilities"] +\
                                                 self.nvda_BS["convertible debt, short-term"] + self.nvda_BS["long-term debt"] +\
                                                 self.nvda_BS["other long-term liabilities"] +  self.nvda_BS["capital lease obligations, long term"]
        except:
            pass

    def lower(self,str):
        return str.lower()

    def get_analysis(self):
        sns.set_style("darkgrid")
        try:
            self.nvda_BS[["total assets", "total liabilities", "total shareholders' equity"]].plot()
            plt.title("Total trend in Liability & Assets and Equity")
            plt.savefig(os.path.join(self.path,"Total_trend.jpg"))
        except:
            self.nvda_BS[["total assets", "total liabilities", "total equity"]].plot()
            plt.title("Total trend in Liability & Assets and Equity")
            plt.savefig(os.path.join(self.path,"Total_trend.jpg"))
 

    def get_liability_column(self,df):
        flag = False
        columns_list = df.columns.tolist()
        columns_list_low = [i.lower() for i in columns_list]
        self.nvda_BS.columns = columns_list_low
        liab_in = columns_list_low.index("liabilities")
        Equity_in = columns_list_low.index("total liabilities") + 1
        liability_columns = columns_list_low[liab_in:Equity_in]
        updated_columns = self.filter_nonvar_columns(liability_columns)
        return [i for i in updated_columns if not('total' in i)], [i for i in updated_columns if('total' in i)]
    
    def get_asset_columns(self,df):
        flag = False
        columns_list = df.columns.tolist()
        columns_list_low = [i.lower() for i in columns_list]
        self.nvda_BS.columns = columns_list_low
        liab_in = columns_list_low.index("liabilities")
        assets_columns = columns_list_low[0:liab_in]
        return [i for i in assets_columns if not('total' in i)], [i for i in assets_columns if('total' in i)]

    def get_equity_columns(self,df):
        columns_list = df.columns.tolist()
        columns_list_low = [i.lower() for i in columns_list]
        self.nvda_BS.columns = columns_list_low
        Equity_in = columns_list_low.index("total liabilities") + 1
        equity_columns = columns_list_low[Equity_in:]
        updated_columns = self.filter_nonvar_columns(equity_columns)
        return [i for i in updated_columns if not('total' in i)], [i for i in updated_columns if('total' in i)]

    def filter_nonvar_columns(self,columns_list):
        var_column_list = []
        for i in columns_list:
            if (self.nvda_BS[i] == 0).all():
                continue
            elif (self.nvda_BS[i] == 0).all():
                continue
            elif(np.std(self.nvda_BS[i]) == 0.0):
                continue
            else:
                var_column_list.append(i)
        return var_column_list
    

    def get_assets_visualize(self):
        asset_columns, total_assets_columns = self.get_asset_columns(self.nvda_BS)
        updated_column_list = self.filter_nonvar_columns(asset_columns)
        if len(asset_columns)%2 == 0:
            fig, ax = plt.subplots(1,2,sharex=True)
            fig.set_figheight(10)
            fig.set_figwidth(15)
            self.nvda_BS[updated_column_list[:len(updated_column_list)//2]].plot(ax=ax[0])
            self.nvda_BS[updated_column_list[len(updated_column_list)//2:]].plot(ax=ax[1])
            plt.suptitle("Trends in the assets Categories of the balance sheet")
            plt.savefig(os.path.join(self.path,"trend_graph.jpg"))
        else:
            fig, ax = plt.subplots(1,2,sharex=True)
            fig.set_figheight(10)
            fig.set_figwidth(15)
            self.nvda_BS[updated_column_list[:len(updated_column_list)//3]].plot(ax=ax[0])
            self.nvda_BS[updated_column_list[len(updated_column_list)//3:]].plot(ax=ax[1])
            plt.suptitle("Trends in the assets Categories of the balance sheet")
            plt.savefig(os.path.join(self.path,"trend_graph.jpg"))


    def get_total_visualize(self):
       

        assets = go.Bar(
            x=self.nvda_BS.index,
            y=self.nvda_BS["total assets"],
            name='Assets'
        )
        liabilities = go.Bar(
            x=self.nvda_BS.index,
            y=self.nvda_BS["total liabilities"],
            name='Liabilities'
        )

        try:
            y = self.nvda_BS["total shareholders' equity"]
        except:
            y = self.nvda_BS['total equity']

        shareholder_equity = go.Scatter(
            x=self.nvda_BS.index,
            y=self.nvda_BS["total shareholders' equity"],
            name='Equity'
        )

        data = [assets, liabilities, shareholder_equity]
        layout = go.Layout(
            barmode='stack'
        )

        fig_bs = go.Figure(data=data, layout=layout)
        py.iplot(fig_bs, filename='Total Assets and Liabilities')
        pio.write_image(fig_bs,os.path.join(self.path,"total.jpg"))

    def get_assets_liab_breakdown(self):
        asset_data = []
        columns, _ = self.get_asset_columns(self.nvda_BS) 


        for col in columns:
            asset_bar = go.Bar(
                x=self.nvda_BS.index,
                y=self.nvda_BS[ col ],
                name=col
            )    
            asset_data.append(asset_bar)
            
        layout_assets = go.Layout(
            barmode='stack'
        )

        fig_bs_assets = go.Figure(data=asset_data, layout=layout_assets)
        py.iplot(fig_bs_assets, filename='Total Assets Breakdown')
        pio.write_image(fig_bs_assets,os.path.join(self.path,"assets_break.jpg"))


        liability_data = []
        columns, _ = self.get_liability_column(self.nvda_BS)


        for col in columns:
            liability_bar = go.Bar(
                x=self.nvda_BS.index,
                y=self.nvda_BS[ col ],
                name=col
            )    
            liability_data.append(liability_bar)
            
        layout_liabilitys = go.Layout(
            barmode='stack'
        )

        fig_bs_liabilitys = go.Figure(data=liability_data, layout=layout_liabilitys)
        py.iplot(fig_bs_liabilitys, filename='Total liabilitys Breakdown')
        pio.write_image(fig_bs_liabilitys,os.path.join(self.path,"liab_break.jpg"))

    def get_other_visualize(self):
        
        self.nvda_BS["working capital"] = self.nvda_BS["total current assets"] - self.nvda_BS["total current liabilities"]
        self.nvda_BS["working capital"].plot()
        self.nvda_BS[["accounts receivable, net", "accounts payable"]].plot()
        self.nvda_BS["inventories"].plot()
        self.nvda_BS[ ["property and equipment, net", "goodwill", "intangible assets, net"] ].plot()
        plt.title("Factor Trend Breakdown")
        plt.savefig(os.path.join(self.path,"trend_brak.jpg"))

    def get_equity_visualize(self):
        
        equity_columns, _ = self.get_equity_columns(self.nvda_BS)
        equity_columns = [ x for x in equity_columns]
        self.nvda_BS[ equity_columns ].plot()
        plt.title("Trend in equity factors")
        plt.savefig(os.path.join(self.path,"equity_trend.jpg"))

    def get_book_val_visualize(self):

        # BV = Total Assets - Intangible assets - Liabilities - Preferred Stock Value
        book_val_dict = {}
        for i in ['total assets','intangible assets, net','goodwill','total liabilities','preferred stock']:
            try:
                book_val_dict[i] = self.nvda_BS[i]
            except:
                book_val_dict[i] = 0
            
        self.nvda_BS["book value"] = book_val_dict["total assets"] - (book_val_dict["intangible assets, net"] \
                                                                      + book_val_dict["goodwill"]) - book_val_dict["total liabilities"]\
                                                                      - book_val_dict["preferred stock"]
        self.nvda_BS["book value"].plot()
        plt.title("Book value")
        plt.savefig(os.path.join(self.path,"Book_fig.jpg"))


    def get_current_ratio_plot(self):

        self.nvda_BS["current ratio"] = self.nvda_BS["total current assets"] / self.nvda_BS["total current liabilities"]
        self.nvda_BS["current ratio"].plot()
        plt.title("Current ratio Trend")
        plt.savefig(os.path.join(self.path,"current.jpg"))


    def get_outlier_points(self):
        
        clf_name = 'KNN'
        clf = KNN()
        clf.fit(self.nvda_BS)
        y_train_pred = clf.labels_  # binary labels (0: inliers, 1: outliers)
        y_train_scores = clf.decision_scores_
        outliers = []
        for i in range(len(y_train_pred)):
            if y_train_pred[i] == 1:
                outliers.append((self.nvda_BS.iloc[i].to_dict(),self.nvda_BS.iloc[i].name))
              
        return outliers

    def visualize_the_outlier(self):
        assets_col, total_assets_col = self.get_asset_columns(self.nvda_BS)
        liability_col, total_liab_col = self.get_liability_column(self.nvda_BS)
        equity_column,total_equity_cols = self.get_equity_columns(self.nvda_BS)
        
        plt_titles = ['Liability Distribution','Equity Distribution']
        for i,j in enumerate([liability_col,equity_column]):
            fig = plt.figure(figsize=(14,10))
        
            sns.boxplot(data= self.nvda_BS[j],orient='h',)
            plt.xticks(rotation=90)
            plt.title(plt_titles[i])
            plt.savefig(os.path.join(self.path,"graph{}.jpg".format(str(i+1))))
        
        fig1, ax = plt.subplots(2,1)
        fig1.set_figwidth(10)
        fig1.set_figheight(14)
        
        plt.subplot(2,1,1)
        sns.boxplot(data=self.nvda_BS[assets_col[:4]],orient='h')
        
        plt.subplot(2,1,2)
        sns.boxplot(data=self.nvda_BS[assets_col[4:]],orient='h')
        plt.suptitle('Assets Distribution')
        plt.savefig(os.path.join(self.path,"assets.jpg"))
            
        fig2, ax = plt.subplots(2,1)
        fig2.set_figwidth(10)
        fig2.set_figheight(14)
        
        plt.subplot(2,1,1)
        ax = sns.boxplot(data=self.nvda_BS[total_assets_col + total_liab_col],orient='h')
        sns.swarmplot(data=self.nvda_BS[total_assets_col + total_liab_col],orient='h',ax=ax,zorder=.5)

        plt.subplot(2,1,2)
        ax = sns.boxplot(data=self.nvda_BS[total_equity_cols[:-3]],orient='h')
        sns.swarmplot(data=self.nvda_BS[total_equity_cols[:-3]],orient='h',ax=ax,zorder=.5)

        plt.suptitle('Total Distribution')
        plt.savefig(os.path.join(self.path,"outlier.jpg"))


def makePdf():
    
    from os import listdir
    path = os.path.join(r"C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\result",\
                        os.listdir(r"C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\result")[-1]) # get the path of images
    imagelist = listdir(path) 
    pdf = FPDF('P','mm','A4')  
    x,y,w,h = 0,0,200,250
    for image in imagelist:

        pdf.add_page()
        pdf.image(os.path.join(path,image),x,y,w,h)

    if os.path.exists(r"C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\report"):
        output = r'C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\report'
        pdf.output(os.path.join(output,"output.pdf"),"F")

    else:
        os.mkdir(r"C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\report")
        output = r'C:\Users\UBAID USMANI\Desktop\CPA_Automation\Bot_UI\report'
        pdf.output(os.path.join(output,"output.pdf"),"F")





def main(file_name,outlier = False):

    if outlier:
        obj = Analysis(file_name,outlier)
        obj.preprocess()
        outliers = obj.get_outlier_points()
        return outliers
    
    else:
        obj = Analysis(file_name,outlier)
        obj.preprocess()
        obj.get_analysis()
        obj.get_assets_visualize()
        obj.get_total_visualize()
        obj.get_assets_liab_breakdown()
        obj.get_equity_visualize()
        obj.get_book_val_visualize()
        obj.get_current_ratio_plot()
        obj.visualize_the_outlier()
        makePdf()


if __name__ == "__main__":

    file_name = input("enter file name:")
    main(file_name)


