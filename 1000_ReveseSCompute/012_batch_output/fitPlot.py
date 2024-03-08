from scipy.special import expit
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import AutoMinorLocator, MultipleLocator, FuncFormatter



def figParaRevers(dic,centerName):
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(3.5,2.625),dpi=200)

    ax.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax.tick_params("x",which = "major",direction = "in" ,
                                        length=3,width = 0.5,labelrotation=0,labelsize=6)
    ax.tick_params("x",which = "minor",direction = "in",
                            length=1.5,width = 0.5 ,labelsize=6)

    ax.set_xlim(0,31)
    ax.set_ylim(0,1)
    #ax.set_xticklabels(a,size=6)
    ax.yaxis.set_minor_locator(AutoMinorLocator(4))
    ax.tick_params("y",which = "major",direction = "in",
                            length=3,width = 0.5 ,labelsize=6)
    ax.tick_params("y",which = "minor",direction = "in",
                            length=1.5,width = 0.5 ,labelsize=6)
    labels = ax.get_xticklabels() + ax.get_yticklabels()
    label = [label.set_fontname('Times New Roman') for label in labels]

    font1 = {'family' : 'Times New Roman',
        'weight' : 'normal',
        'size'   : 6}

    ax.set_xlabel("Distance to the city center(km)",font1,size=7)
    ax.set_ylabel("Urban land density",font1,size=7)
    ax.set_title(centerName,font1,size=8)

    color = ["r","lawngreen","b","coral","g","lightskyblue","m","deeppink"]
    i=0
    acd = {}
    for year,data in dic.items():
        y1 = data.loc[:,"dens"]
        x1 = y1.index+1
        ax.plot(x1,y1,".",c=color[i],ms = 2)
        a,c,d,yvals = reverseSFit(x1,y1)
        ax.plot(x1,yvals,"--",lw=1,c=color[i],label = str(year))
        ax.legend(prop=font1,frameon=False,loc="lower left")
        i+=1

        acd[year]=np.round([a,c,d],4)

    return fig,acd

def figParaGMP(dic,centerName):
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(3.5,2.625),dpi=200)

    ax.xaxis.set_minor_locator(AutoMinorLocator(4))
    ax.tick_params("x",which = "major",direction = "in" ,
                                        length=3,width = 0.5,labelrotation=0,labelsize=6)
    ax.tick_params("x",which = "minor",direction = "in",
                            length=1.5,width = 0.5 ,labelsize=6)

    ax.set_xlim(0,31)
    ax.set_ylim(0,1)
    #ax.set_xticklabels(a,size=6)
    ax.yaxis.set_minor_locator(AutoMinorLocator(4))
    ax.tick_params("y",which = "major",direction = "in",
                            length=3,width = 0.5 ,labelsize=6)
    ax.tick_params("y",which = "minor",direction = "in",
                            length=1.5,width = 0.5 ,labelsize=6)
    labels = ax.get_xticklabels() + ax.get_yticklabels()
    label = [label.set_fontname('Times New Roman') for label in labels]

    font1 = {'family' : 'Times New Roman',
        'weight' : 'normal',
        'size'   : 6}

    ax.set_xlabel("Distance to the city center(km)",font1,size=7)
    ax.set_ylabel("Urban land density",font1,size=7)
    ax.set_title(centerName,font1,size=8)

    color = ["r","lawngreen","b","coral","g","lightskyblue","m","deeppink"]
    i=0
    an = {}
    for year,data in dic.items():
        y = data.loc[:,"dens"]
        x = y.index+1
        ax.plot(x,y,".",c=color[i],ms = 2)
        a,n,yvals = gmpFit(x,y)
        ax.plot(x,yvals,"--",lw=1,c=color[i],label = str(year))
        ax.legend(prop=font1,frameon=False,loc="lower left")
        i+=1

        an[year]=np.round([a,n],4)

    return fig, an
def reverseSFit(x,y):
    def reverseS(x1, a, c, d):
        y1 = (1-c)/(1+expit( a*(2*x1/d-1) ))+c # overflow-error-in-pythons-numpy-exp-function
        return y1
    popt, pcov = curve_fit(reverseS, x, y)#, maxfev=5000

    # popt
    a = popt[0]
    c = popt[1]
    d = popt[2]
    yvals = reverseS(x,a,c,d) #拟合y值

    #print(pcov)

    return a,c,d,yvals

def gmpFit(x,y):
    def gmp(x1, alpha, n):
        y1 = 1-(1-x1**(-alpha))**n
        return y1
    popt, pcov = curve_fit(gmp, x, y)#maxfev=5000

    #popt
    alpha = popt[0]
    n = popt[1]
    yvals = gmp(x,alpha,n) #拟合y值

    #print(pcov)

    return alpha,n,yvals

def main():
    dic = {}
    for year, group_data in df.groupby("year"):
        if len(group_data)>=5:
            dic[year] = group_data.reset_index(drop=True)

    if status >0:
        fig_rvs, acd = figParaRevers(dic,name)
        figSname = path + "FigS_"+name+ file_x +".png"
        fig_rvs.savefig(figSname,bbox_inches="tight",dpi=1200,pad_inches=0)

        df_acd = pd.DataFrame(acd)
        acdname = path+"ACD_"+name+ file_x +".csv"
        df_acd.to_csv(acdname)

    if status >1:
        fig_gmp, an = figParaGMP(dic,name)
        figGname = path + "FigG_"+name+ file_x +".png"
        fig_gmp.savefig(figGname,bbox_inches="tight",dpi=1200,pad_inches=0)

        df_an = pd.DataFrame(an)
        anname = path+"AN_"+name+ file_x +".csv"
        df_an.to_csv(anname)
