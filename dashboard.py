import streamlit as st
import pandas as pd
import plotly.express as px

#config 
st.set_page_config(page_title="Scotland Housing Price Trends", layout="centered", initial_sidebar_state='expanded')
#colour palette
custom = ["#1cd252","#ff2f00","#4874EC","#ffbb00",'#984ea3','#ffff33']


# CSS for centering metric etc. (streamlit is left aligned by default)
# and add metric background
st.markdown("""
    <style>
    /* Centers the entire metric container */
    [data-testid="stMetric"] {
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* Centers the Label (RegionName) */
    [data-testid="stMetricLabel"] {
        display: flex;
        justify-content: center;
        width: 100%;
    }

    /* Centers the Value (The Price) */
    [data-testid="stMetricValue"] {
        display: flex;
        justify-content: center;
        width: 100%;
    }

    /* Centers the Delta (The % Change) */
    [data-testid="stMetricDelta"] {
        display: flex;
        justify-content: center;
        width: 100%;
    }
        
    
    /* Targeting the metric container for the outline */
    [data-testid="stMetric"] {
        border: 1px solid #4B4B4B; 
        padding: 15px;             
        border-radius: 10px;       
        background-color: #1E1E1E; /* Dark background */
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3); 
        transition: transform 0.2s; 
    }

    </style>
    """, unsafe_allow_html=True)

#cache for faster loading
@st.cache_data
def get_data():
    df = pd.read_csv('scot_housing_2005_clean.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = get_data()





## SIDEBAR Filters
st.sidebar.header("Filter Options")
# By Region
regions = st.sidebar.multiselect(
    "Local Authorities",
    options=sorted(df['RegionName'].unique()),
    default=['Scotland', 'City of Edinburgh', 'City of Glasgow'],
    help="You can compare multiple regions simultaneously."
)

st.sidebar.divider()

# By Timeframe
df['Year'] = df['Date'].dt.year
min_year = int(df['Year'].min())
max_year = int(df['Year'].max())


st.sidebar.subheader("Timeframe")
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year), # Default to the full range
    step=1,
    help="Slide to focus on specific timeframe (e.g. 2008 Housing Crash or 2019 Pandemic)"
)

st.sidebar.divider()


# Filter the data based on above filters
mask = (df['RegionName'].isin(regions)) & \
       (df['Year'] >= year_range[0]) & \
       (df['Year'] <= year_range[1])

df_filtered = df[mask].copy()


#If not filters selected, throw correct error
if df_filtered.empty:
    st.error("⚠️ No data available for this combination of regions and dates. Try adjusting your filters.")
    st.stop()


# Introduction
st.title(" Scottish Housing Index Dashboard :house:")
latest_date_in_range = df_filtered['Date'].max()
latest_df = df_filtered[df_filtered['Date'] == latest_date_in_range]

st.markdown("""
Hello! My name is Darragh Coyle. I’m an aspiring data scientist currently studying MSc in Big Data at University of Stirling :deciduous_tree:
            
This dashboard is personal project to help visualise available data on Scotland Housing Prices across all Scottish Constituencies (as I still hold the optimistic view I will own property myself someday!)    
               
 
**Data Source:** [UK Government Housing Price Index](https://www.gov.uk/government/statistical-data-sets/uk-house-price-index-data-downloads-december-2025)
            
""")

st.space()

#LATEST DATA 
st.info(f"**Data only available from January 2005 -- {df['Date'].max().strftime('%B %Y')}**", icon = "💡")

st.space()

st.markdown("Check out my [Linkedin](https://www.linkedin.com/in/darragh-coyle/) and [Github](https://github.com/dara86) (+ source [code](https://github.com/dara86/scottish-housing-dashboard))")          

st.divider()




# Average Price by region
st.header("Average Property Price", text_alignment="center")
st.markdown(f"Current Data: **{df_filtered['Date'].max().strftime('%Y')}**")
st.space("medium")

# Average Price Metrics, 3 per row
num_cols = min(len(regions), 3)
cols = st.columns(num_cols)

# get average price + YoY % change for each metric
for i, region in enumerate(regions):
    region_data = latest_df[latest_df['RegionName'] == region]
    if not region_data.empty:
        price = region_data['AveragePrice'].values[0]
        change = region_data['Yearly%Change'].values[0]
        
        cols[i % num_cols].metric(
            label=region, 
            value=f"£{price:,.0f}", 
            delta=f"{change:.1f}% Year-on-Year"
        )

st.space("small")

#  


# Chart: Average Price over Time
st.divider()
st.markdown(""" \
## Average Property Price Over Time""", text_alignment="center")

st.info("**Use Local Authority Filter to adjust Region of interest**" , icon = "⬅️")

st.space("medium")

fig_price = px.line(
    df_filtered, 
    x='Date', 
    y='AveragePrice', 
    color='RegionName',
    template="plotly_dark",
    color_discrete_sequence=custom,
    labels={"AveragePrice": "Price (£)",
            "RegionName":"Region"}
)
st.plotly_chart(fig_price, use_container_width=True)
st.divider()





# Property Type Comparison 
st.header("Average Prices by Property Type", text_alignment = "center")

st.info("**Use Timeframe Filter to adjust year of interest**" , icon = "⬅️")
st.space()
st.markdown(f"Current Data: **{df_filtered['Date'].max().strftime('%Y')}**")
# Create the selection options
column_options = {
    "FlatPrice":"Flats",
    "DetachedPrice": "Detached Houses",
    "SemiDetachedPrice": "Semi-Detached House",
   "NewPrice": "New Builds",
    "OldPrice":"Existing Properties"
}



# Melt the data to make it 'Long' format 
df_melted = latest_df.melt(
    id_vars=['RegionName'], 
    value_vars=['FlatPrice', 'SemiDetachedPrice','DetachedPrice'],
    var_name='Property Type', 
    value_name='Price'
)

# After melting, replace the strings in the 'Property Type' column
df_melted['Property Type'] = df_melted['Property Type'].map({
    "FlatPrice": "Flat ",
    "SemiDetachedPrice": "Semi-Detached ",
    "DetachedPrice": "Detached"
})

# fig: grouped bar chart
fig_gap = px.bar(
    df_melted, 
    x='RegionName', 
    y='Price', 
    color='Property Type',
    template="plotly_dark",
    color_discrete_sequence=custom,
    barmode='group',
    opacity=0.85,
    
    labels={"Price": "Price (£)", "RegionName": "Region"}
)
st.plotly_chart(fig_gap, use_container_width=True)

st.divider()





#historical performance section
st.header("Historical Performance", text_alignment='center')
st.markdown("Best and Worst Performing 12-month period", text_alignment='center')
st.markdown("")

st.space("xxsmall")

num_cols = min(len(regions), 3)
perf_cols = st.columns(num_cols)


for i, region in enumerate(regions):
    reg_data = df_filtered[df_filtered['RegionName'] == region]
    
    if not reg_data.empty:
        # Find the best and worst rows
        best_row = reg_data.loc[reg_data['Yearly%Change'].idxmax()]
        worst_row = reg_data.loc[reg_data['Yearly%Change'].idxmin()]
        
        #Function to create the date range
        def get_range(end_date):
            # Calculate the start date 
            start_date = end_date - pd.DateOffset(months=12)
            # Format: "May 2005 - May 2006"
            return f"{start_date.strftime('%b %Y')} – {end_date.strftime('%b %Y')}"

        with perf_cols[i % num_cols]:
            st.markdown(f"<h4 style='text-align: center; margin-top:20px;'>{region}</h4>", unsafe_allow_html=True)
            
            st.space()
            # Show the High
            st.metric(
                label=f"{get_range(best_row['Date'])}",
                value=f"{best_row['Yearly%Change']:.1f}%",
                delta="Historic Peak"
            )
            st.space('small')
            # Show the Low
            st.metric(
             label=f" {get_range(worst_row['Date'])}",
             value=f"{worst_row['Yearly%Change']:.1f}%",
             delta="Historic Low",
             delta_color="inverse",
             delta_arrow="down"
    )


st.space('small')

st.divider()




## New builds vs. Existing build  
st.header("New Builds vs. Existing Properties", text_alignment = "center")
st.markdown("Hover over to see 'Percentage Difference' between Newly-built properties and Existing properties", text_alignment='center')


st.space("medium")


# calculate the % difference (premium) for new property vs. old
# done before melting
df_calc = df_filtered.copy()
df_calc['Premium_%'] = ((df_calc['NewPrice'] - df_calc['OldPrice']) / df_calc['OldPrice']) * 100
df_calc['Premium_%'] = pd.to_numeric(df_calc['Premium_%'], errors='coerce')
# rounding to 1 decimal place
df_calc['Premium_%'] = df_calc['Premium_%'].round(1)

# Melt for the Line Chart
# + include 'Premium %' in id_vars so it stays attached to every row
df_trend_long = df_calc.melt(
        id_vars=['Date', 'RegionName', 'Premium_%'],
        value_vars=['NewPrice', 'OldPrice'],
        var_name='Market Segment',
        value_name='Price'
    )

#clean labels
df_trend_long['Market Segment'] = df_trend_long['Market Segment'].map({
        "NewPrice": "New Build",
        "OldPrice": "Existing Property"
    })



 # Create plot
fig_vertical = px.line(
    df_trend_long,
    x='Date',
    y='Price',
    color='Market Segment',
    color_discrete_map={
        "New Build": "#fa0000",       
        "Existing Property": "#0eb83c"  
    },
    facet_row='RegionName', 
    facet_row_spacing=0.12, # Increased spacing to make room for X-axis labels
    template="plotly_dark",
    custom_data=['Premium_%'],
    labels={"Price": "Price (£)", "Date": ""}
)

# Independent X and Y Axes
fig_vertical.update_yaxes(matches=None, showticklabels=True)
fig_vertical.update_xaxes(matches=None, showticklabels=True)

# clean hovering data layout 
for trace in fig_vertical.data:
    if "New Build" in trace.name:
        # :+ forces the + or - sign / <extra></extra> removes label when hovering
        trace.hovertemplate = "New Build: £%{y:,.0f}<br><b>Percentage Difference %{customdata[0]:+}%</b><extra></extra>"
    else:
        trace.hovertemplate = "Existing: £%{y:,.0f}<extra></extra>"

# Layout Polishing
fig_vertical.update_layout(
    hovermode="x unified",
    height=450 * len(regions), # Slightly taller to accommodate  labels
    legend=dict(
        orientation="h",    
        yanchor="bottom",    
        y=1.05,              
        x=0.5,               
        xanchor="left",    
        title_text="" ,
        font=dict(size=20)       
    ),
    
)


# titles 
fig_vertical.for_each_annotation(lambda a: a.update(
    text=f"<b>{a.text.split('=')[-1]}</b>", #removes 'RegionName='
    x=0.5,               # Horizontal center
    xanchor='center',    
    yanchor='bottom',    
    yshift=115,           # Pushes the text UP 
    textangle=0,        
    font=dict(size=18)
))

st.plotly_chart(fig_vertical, use_container_width=True)

st.divider()

            
