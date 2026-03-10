import axios from 'axios'

export interface CensusData {
	total_enr: number

	// Add other census fields as they become available
	[key: string]: any
}

export interface CensusDataById {
	census_data_id: string
	academic_year: number
	aggregation_level: string
	county_code: string
	district_code: string
	school_code: string
	county_name: string
	district_name: string
	school_name: string
	charter: string
	reporting_category: string
	total_enr: number
	gr_tk: number
	gr_kn: number
	gr_1: number
	gr_2: number
	gr_3: number
	gr_4: number
	gr_5: number
	gr_6: number
	gr_7: number
	gr_8: number
	gr_9: number
	gr_10: number
	gr_11: number
	gr_12: number
}

export interface CensusDataResponse {
	data: CensusData
	status: string
}

export interface CensusDataByIdResponse {
	data: CensusDataById
	status: string
}

export class CensusService {
	/**
	 * Get Census Data
	 * Retrieve census data including total enrollment.
	 * @returns CensusDataResponse Successful Response
	 * @throws ApiError
	 */
	public static async getCensusData(): Promise<CensusDataResponse> {
		const response = await axios.get<CensusDataResponse>('/api/v1/censusdata')
		return response.data
	}

	/**
	 * Get Census Data By ID
	 * Retrieve specific census data by ID.
	 * @param id The census data ID
	 * @returns CensusDataByIdResponse Successful Response
	 * @throws ApiError
	 */
	public static async getCensusDataById(id: string): Promise<CensusDataByIdResponse> {
		const response = await axios.get<CensusDataByIdResponse>(`/api/v1/censusdata/${id}`)
		return response.data
	}
}
