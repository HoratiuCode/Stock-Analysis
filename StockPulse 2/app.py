import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io

st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #fafafa;
    }
    .stMetric {
        background-color: #262730;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Stock Analysis Dashboard")
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    stock_symbol = st.text_input(
        "Enter Symbol (Stock or Crypto)",
        value="AAPL",
        help="Enter a valid stock ticker (e.g., AAPL, TSLA) or crypto pair (e.g., BTC-USD, ETH-USD)"
    ).upper()

with col2:
    time_period = st.selectbox(
        "Time Period",
        options=["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"],
        index=1,
        help="Select the time period for historical data"
    )

if stock_symbol:
    try:
        with st.spinner(f"Fetching data for {stock_symbol}..."):
            stock = yf.Ticker(stock_symbol)
            
            info = stock.info
            hist = stock.history(period=time_period)
            
            if hist.empty or not info:
                st.error(f"❌ No data found for symbol: {stock_symbol}. Please enter a valid stock ticker.")
            else:
                st.success(f"✅ Data loaded for {info.get('longName', stock_symbol)}")
                
                col1, col2, col3, col4, col5 = st.columns(5)
                
                current_price = hist['Close'].iloc[-1]
                prev_close = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else current_price)
                price_change = current_price - prev_close
                price_change_pct = (price_change / prev_close) * 100 if prev_close else 0
                
                with col1:
                    st.metric(
                        "Current Price",
                        f"${current_price:.2f}",
                        f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
                    )
                
                with col2:
                    market_cap = info.get('marketCap', 0)
                    if market_cap >= 1e12:
                        market_cap_str = f"${market_cap/1e12:.2f}T"
                    elif market_cap >= 1e9:
                        market_cap_str = f"${market_cap/1e9:.2f}B"
                    elif market_cap >= 1e6:
                        market_cap_str = f"${market_cap/1e6:.2f}M"
                    else:
                        market_cap_str = f"${market_cap:,.0f}"
                    st.metric("Market Cap", market_cap_str)
                
                with col3:
                    pe_ratio = info.get('trailingPE', 'N/A')
                    pe_display = f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio
                    st.metric("P/E Ratio", pe_display)
                
                with col4:
                    day_high = hist['High'].iloc[-1]
                    st.metric("Day High", f"${day_high:.2f}")
                
                with col5:
                    day_low = hist['Low'].iloc[-1]
                    st.metric("Day Low", f"${day_low:.2f}")
                
                st.markdown("---")
                
                tab1, tab2, tab3 = st.tabs(["📊 Price Chart", "📋 Financial Data", "💹 Volume Chart"])
                
                with tab1:
                    st.subheader(f"{stock_symbol} Stock Price")
                    
                    chart_type = st.radio(
                        "Chart Type",
                        options=["Candlestick", "Line"],
                        horizontal=True
                    )
                    
                    fig = go.Figure()
                    
                    if chart_type == "Candlestick":
                        fig.add_trace(go.Candlestick(
                            x=hist.index,
                            open=hist['Open'],
                            high=hist['High'],
                            low=hist['Low'],
                            close=hist['Close'],
                            name=stock_symbol
                        ))
                    else:
                        fig.add_trace(go.Scatter(
                            x=hist.index,
                            y=hist['Close'],
                            mode='lines',
                            name='Close Price',
                            line=dict(color='#00d4ff', width=2)
                        ))
                    
                    fig.update_layout(
                        template='plotly_dark',
                        height=500,
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        hovermode='x unified',
                        showlegend=True,
                        plot_bgcolor='#0e1117',
                        paper_bgcolor='#0e1117',
                        font=dict(color='#fafafa')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    st.subheader("Key Financial Metrics")
                    
                    financial_data = {
                        'Metric': [
                            'Company Name',
                            'Symbol',
                            'Sector',
                            'Industry',
                            'Current Price',
                            'Previous Close',
                            'Open',
                            'Day High',
                            'Day Low',
                            '52 Week High',
                            '52 Week Low',
                            'Volume',
                            'Average Volume',
                            'Market Cap',
                            'P/E Ratio (Trailing)',
                            'P/E Ratio (Forward)',
                            'EPS (Trailing)',
                            'Dividend Yield',
                            'Beta',
                            'Total Revenue',
                            'Total Cash',
                            'Total Debt'
                        ],
                        'Value': [
                            info.get('longName', 'N/A'),
                            stock_symbol,
                            info.get('sector', 'N/A'),
                            info.get('industry', 'N/A'),
                            f"${current_price:.2f}",
                            f"${info.get('previousClose', 'N/A')}" if info.get('previousClose') else 'N/A',
                            f"${info.get('open', 'N/A'):.2f}" if info.get('open') else 'N/A',
                            f"${day_high:.2f}",
                            f"${day_low:.2f}",
                            f"${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}" if info.get('fiftyTwoWeekHigh') else 'N/A',
                            f"${info.get('fiftyTwoWeekLow', 'N/A'):.2f}" if info.get('fiftyTwoWeekLow') else 'N/A',
                            f"{hist['Volume'].iloc[-1]:,.0f}" if len(hist) > 0 else 'N/A',
                            f"{info.get('averageVolume', 'N/A'):,.0f}" if info.get('averageVolume') else 'N/A',
                            market_cap_str,
                            f"{info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get('trailingPE'), (int, float)) else 'N/A',
                            f"{info.get('forwardPE', 'N/A'):.2f}" if isinstance(info.get('forwardPE'), (int, float)) else 'N/A',
                            f"{info.get('trailingEps', 'N/A'):.2f}" if isinstance(info.get('trailingEps'), (int, float)) else 'N/A',
                            f"{info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else 'N/A',
                            f"{info.get('beta', 'N/A'):.2f}" if isinstance(info.get('beta'), (int, float)) else 'N/A',
                            f"${info.get('totalRevenue', 0)/1e9:.2f}B" if info.get('totalRevenue') else 'N/A',
                            f"${info.get('totalCash', 0)/1e9:.2f}B" if info.get('totalCash') else 'N/A',
                            f"${info.get('totalDebt', 0)/1e9:.2f}B" if info.get('totalDebt') else 'N/A'
                        ]
                    }
                    
                    df_financial = pd.DataFrame(financial_data)
                    st.dataframe(df_financial, use_container_width=True, height=400)
                    
                    csv = df_financial.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Financial Data as CSV",
                        data=csv,
                        file_name=f"{stock_symbol}_financial_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )
                    
                    st.markdown("---")
                    st.subheader("Historical Price Data")
                    
                    hist_display = hist.copy()
                    hist_display.index = hist_display.index.strftime('%Y-%m-%d')
                    hist_display = hist_display.round(2)
                    
                    st.dataframe(hist_display, use_container_width=True, height=300)
                    
                    csv_hist = hist_display.to_csv().encode('utf-8')
                    st.download_button(
                        label="📥 Download Historical Data as CSV",
                        data=csv_hist,
                        file_name=f"{stock_symbol}_historical_data_{time_period}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                    )
                
                with tab3:
                    st.subheader(f"{stock_symbol} Trading Volume")
                    
                    fig_volume = go.Figure()
                    
                    colors = ['#00d4ff' if hist['Close'].iloc[i] >= hist['Open'].iloc[i] 
                             else '#ff4b4b' for i in range(len(hist))]
                    
                    fig_volume.add_trace(go.Bar(
                        x=hist.index,
                        y=hist['Volume'],
                        name='Volume',
                        marker_color=colors
                    ))
                    
                    fig_volume.update_layout(
                        template='plotly_dark',
                        height=400,
                        xaxis_title="Date",
                        yaxis_title="Volume",
                        hovermode='x unified',
                        plot_bgcolor='#0e1117',
                        paper_bgcolor='#0e1117',
                        font=dict(color='#fafafa')
                    )
                    
                    st.plotly_chart(fig_volume, use_container_width=True)
                
                with st.expander("ℹ️ Company Information"):
                    st.write(f"**Company:** {info.get('longName', 'N/A')}")
                    st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                    st.write(f"**Industry:** {info.get('industry', 'N/A')}")
                    st.write(f"**Website:** {info.get('website', 'N/A')}")
                    st.write(f"**Description:** {info.get('longBusinessSummary', 'No description available.')}")
    
    except Exception as e:
        st.error(f"❌ Error fetching data: {str(e)}")
        st.info("💡 Please check the stock symbol and try again. Make sure it's a valid ticker symbol (e.g., AAPL, GOOGL, MSFT).")

st.markdown("---")
st.caption("Data provided by Yahoo Finance")
