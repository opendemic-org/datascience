import opendemic.data as odd
import opendemic.modelling as odm


# example 1:
# State of New York
state = 'ny' # it's not case sensitive
ny_region_data = odd.USARegionData.fetch(state=state)

# NOTE: this is not implemented yet
rt_result = odm.compute_rt(ny_region_data.dates, ny_region_data.new_cases)
ny_rt = rt_result[0] # time series of Rt
ny_hdi_low = rt_result[1] # lower boundary of credible interval of Rt
ny_hdi_high = rt_result[2] # higher boundary of credible interval of Rt

# example 2:
# Suffolk county, NY
fips = 36103
county_data = odd.USARegionData.fetch(county=fips)
# then it's the same as for the ny data