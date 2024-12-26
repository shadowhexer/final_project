import axios, { type AxiosInstance } from 'axios';

const getCsrfToken = () => {
  return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
};

const API: AxiosInstance = axios.create({
  baseURL: 'http://127.0.0.1:8000/', // Django backend URL
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': getCsrfToken() // Include CSRF token if needed
  }
});

export default API;