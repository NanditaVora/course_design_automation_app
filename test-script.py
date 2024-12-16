import pandas
import json

print(json.loads("""

[
{
"topic": "Introduction to Time Series",
"sub_topic": "Introduction and Intuition for Stationarity",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Time Series",
"sub_topic": "Meaning and utility of time series",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Stationary Process",
"sub_topic": "Basic properties and linear processes",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "ARMA Models",
"sub_topic": "Introduction to ARMA models",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "ARMA Processes",
"sub_topic": "Properties of sample mean and autocorrelation function",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Forecasting",
"sub_topic": "Forecasting stationary time series",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "ARMA(p, q) Processes",
"sub_topic": "ACF and PACF",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Time Series Estimation",
"sub_topic": "Preliminary estimation",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "N",
"Accept Topic for CTKS": "N"
},
{
"topic": "Maximum Likelihood Estimation",
"sub_topic": "Time series estimation techniques",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "N",
"Accept Topic for CTKS": "N"
},
{
"topic": "Nonstationary Time Series",
"sub_topic": "ARIMA models",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Time Series Identification",
"sub_topic": "Identification techniques",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Unit Roots",
"sub_topic": "Unit roots in time series",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Seasonal Time Series",
"sub_topic": "Seasonal ARIMA models",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Multivariate Time Series",
"sub_topic": "Second-order properties of multivariate time series",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "N",
"Accept Topic for CTKS": "N"
},
{
"topic": "State-Space Models",
"sub_topic": "State-space representations",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "N",
"Accept Topic for CTKS": "N"
},
{
"topic": "Forecasting Techniques",
"sub_topic": "ARAR algorithm",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Autocorrelation",
"sub_topic": "Autocorrelation Functions (ACF)",
"exists_in_college_syllabus": "Y",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Partial Autocorrelation",
"sub_topic": "Partial Autocorrelation Functions (PACF)",
"exists_in_college_syllabus": "N",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Model Selection",
"sub_topic": "Akaike Information Criterion (AIC)",
"exists_in_college_syllabus": "N",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Bayesian Time Series Analysis",
"sub_topic": "Normal Dynamic Linear Models",
"exists_in_college_syllabus": "N",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
},
{
"topic": "Practical Applications",
"sub_topic": "Visualizing Time Series",
"exists_in_college_syllabus": "N",
"exists_in_dump": "N",
"exists_in_competition": "Y",
"Accept Topic for CTKS": "TBD"
}
]

"""))