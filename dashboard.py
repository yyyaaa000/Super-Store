import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore")
#设置界面，横向充满屏幕
st.set_page_config(page_title="Dash Project", page_icon=":bar_chart:", layout="wide")

st.title(" :bar_chart: SuperStore ")
#用markdown插入css样式
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
#上传文件
fl = st.file_uploader(":file_folder: Choose a file", type=(["pdf","csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename,encoding="ISO-8859-1") #设置编码标准
else:
    os.chdir(r"C:\Users\yaoxuemeng\Desktop\2024\coding\dash")
    df = pd.read_csv("Superstore.csv",encoding="ISO-8859-1")

col1, col2 =st.columns((2))
df["Order Date"] = pd.to_datetime(df["Order Date"])
#找到最大和最小的日期，安排column上的日期排序
startd = pd.to_datetime(df["Order Date"].min())
endd = pd.to_datetime(df["Order Date"].max())
with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startd))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endd))
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy() #拷贝一份，不影响原数据

st.sidebar.header("Choose your filter:")
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    dff = df.copy()
else:
    dff = df[df["Region"].isin(region)]

state = st.sidebar.multiselect("Pick your State", dff["State"].unique())
if not state:
    dfff = dff.copy()
else:
    dfff = dff[dff["State"].isin(state)]

city = st.sidebar.multiselect("Pick your City", dfff["City"].unique())

#根据选择的位置、州、城市进行数据保存和删除
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = dfff[df["State"].isin(state) & dfff["City"].isin(city)]
elif region and city:
    filtered_df = dfff[df["Region"].isin(region) & dfff["City"].isin(city)]
elif region and state:
    filtered_df = dfff[df["Region"].isin(region) & dfff["State"].isin(state)]
elif city:
    filtered_df = dfff[dfff["City"].isin(city)]
else:
    filtered_df = dfff[dfff["Region"].isin(region) & dfff["State"].isin(state) & dfff["City"].isin(city)]

#按照 "Category" 列进行分组，并计算每个分类的销售总额
category_df = filtered_df.groupby(by = ["Category"], as_index = False)["Sales"].sum()
with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x = "Category", y = "Sales", text = ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template = "seaborn")#格式化了销售总额为货币形式，并保留了两位小数；template设置模板
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values = "Sales", names = "Region", hole = 0.5)
    fig.update_traces(text = filtered_df["Region"], textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)

#进行数据下载
cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df)
        csv = category_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Category.csv", mime = "text/csv", help = 'Download the data as a CSV file')
with cl2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(region)
        csv = region.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "Region.csv", mime = "text/csv", help = 'Download the data as a CSV file')

#将转换后的结果赋值给名为 "month_year" 的新列，该列将包含每个订单日期对应的年月信息
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')
#%Y:%b转换为指定格式的字符，之后按照日期进行分组，计算每月sales总和，reset_index将结果转化为dataframe，并重新索引
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
#创建一个表格实例,template选择模板样式
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales" : "Amount"}, height=500, width=1000, template="gridon")
#将表格显示在界面中，宽度自适应
st.plotly_chart(fig2, use_container_width=True)
#expander创建一个可展开的区域
with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T) #列-->索引，行-->列名称，转量
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv') #mime规定下载格式，如text/html, text/css

#创建树状图treemap
st.subheader("Hierarchical View of Sales using Treemap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"])
fig3.update_layout(width = 800, height = 650) #指定大小
st.plotly_chart(fig3, use_container_width=True)

#建立饼状图
pie1,pie2 = st.columns((2))
with pie1:
    st.subheader("Segment wise Sales")
    fig = px.pie(filtered_df,values="Sales",names="Segment",template="gridon")
    fig.update_traces(text=filtered_df["Segment"],textposition="inside")
    st.plotly_chart(fig, use_container_width=True)
with pie2:
    st.subheader("Category wise Sales")
    fig = px.pie(filtered_df,values="Sales",names="Category",template="gridon")
    fig.update_traces(text=filtered_df["Category"],textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

#建立散点图
sca = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
sca.update_layout(title="Relationship between Sales and Profits using Scatter Plot", titlefont=dict(size=25))
st.plotly_chart(sca, use_container_width=True)