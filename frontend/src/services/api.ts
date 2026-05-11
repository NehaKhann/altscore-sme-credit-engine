import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8080',
  headers: { 'Content-Type': 'application/json' }
});

export interface BusinessRequest {
  businessName: string;
  ownerName: string;
  businessType: string;
  monthlyRevenue: number;
  yearsInOperation: number;
  numTransactions: number;
}

export interface BusinessResponse {
  id: number;
  businessName: string;
  ownerName: string;
  businessType: string;
  monthlyRevenue: number;
  yearsInOperation: number;
  numTransactions: number;
  creditScore: number;
  riskLevel: string;
  aiExplanation: string;
  aiRecommendations: string;
  createdAt: string;
}

export const createBusiness = (data: BusinessRequest) =>
  api.post<BusinessResponse>('/api/v1/businesses', data);

export const getAllBusinesses = () =>
  api.get<BusinessResponse[]>('/api/v1/businesses');