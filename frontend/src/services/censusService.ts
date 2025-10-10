import { OpenAPI } from '../client/core/OpenAPI';
import { request as __request } from '../client/core/request';
import type { CancelablePromise } from '../client/core/CancelablePromise';

export interface CensusData {
	total_enr: number;
	// Add other census fields as they become available
	[key: string]: any;
}

export interface CensusDataById {
	census_data_id: string;
	academic_year: number;
	aggregation_level: string;
	county_code: string;
	district_code: string;
	school_code: string;
	county_name: string;
	district_name: string;
	school_name: string;
	charter: string;
	reporting_category: string;
	total_enr: number;
	gr_tk: number;
	gr_kn: number;
	gr_1: number;
	gr_2: number;
	gr_3: number;
	gr_4: number;
	gr_5: number;
	gr_6: number;
	gr_7: number;
	gr_8: number;
	gr_9: number;
	gr_10: number;
	gr_11: number;
	gr_12: number;
}

export interface CensusDataResponse {
	data: CensusData;
	status: string;
}

export interface CensusDataByIdResponse {
	data: CensusDataById;
	status: string;
}

export class CensusService {
	/**
	 * Get Census Data
	 * Retrieve census data including total enrollment.
	 * @returns CensusDataResponse Successful Response
	 * @throws ApiError
	 */
	public static getCensusData(): CancelablePromise<CensusDataResponse> {
		return __request(OpenAPI, {
			method: 'GET',
			url: '/api/v1/censusdata',
			errors: {
				404: 'Census data not found',
				422: 'Validation Error',
				500: 'Internal Server Error',
			},
		});
	}

	/**
	 * Get Census Data By ID
	 * Retrieve specific census data by ID.
	 * @param id The census data ID
	 * @returns CensusDataByIdResponse Successful Response
	 * @throws ApiError
	 */
	public static getCensusDataById(
		id: string,
	): CancelablePromise<CensusDataByIdResponse> {
		return __request(OpenAPI, {
			method: 'GET',
			url: `/api/v1/censusdata/${id}`,
			errors: {
				403: 'Not enough permissions',
				404: 'Census data not found',
				422: 'Validation Error',
				500: 'Internal Server Error',
			},
		});
	}
}
