import axios from 'axios';

const getAuthToken = () => localStorage.getItem('token');

const api = axios.create({
  baseURL: 'http://localhost:8080',
  headers: { 'Content-Type': 'application/json' }
});

api.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface AuthResponse {
  token: string;
  email: string;
  fullName: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  fullName: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export const register = (data: RegisterRequest) =>
  api.post<AuthResponse>('/api/v1/auth/register', data);

export const login = (data: LoginRequest) =>
  api.post<AuthResponse>('/api/v1/auth/login', data);

export interface BusinessRequest {
  businessName: string;
  ownerName: string;
  businessType: string;
  monthlyRevenue: number;
  yearsInOperation: number;
  numTransactions: number;
}

export interface LoanMatch {
  bankName: string;
  productName: string;
  logoInitials: string;
  color: string;
  maxLoanAmount: string;
  interestRate: string;
  processingTime: string;
  matchStatus: 'QUALIFIED' | 'ALMOST' | 'NOT_ELIGIBLE';
  matchPercentage: number;
  gaps: string[];
  highlight: string;
  minScore: number;
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
  loanMatches: LoanMatch[];
  qualifiedLoansCount: number;
  almostLoansCount: number;
  createdAt: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

export interface ChatRequest {
  businessId: number;
  message: string;
  history: ChatMessage[];
}

export interface ChatResponse {
  message: string;
  success: boolean;
}

export const createBusiness = (data: BusinessRequest) =>
  api.post<BusinessResponse>('/api/v1/businesses', data);

export const getAllBusinesses = () =>
  api.get<BusinessResponse[]>('/api/v1/businesses');

export const sendChatMessage = (data: ChatRequest) =>
  api.post<ChatResponse>('/api/v1/chat', data);