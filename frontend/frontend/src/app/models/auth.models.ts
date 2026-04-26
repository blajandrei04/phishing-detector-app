export interface User {
  id: string;
  username: string;
  email: string;
  role?: string;
  token?: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterCredentials {
  username: string;
  email: string;
  password: string;
}

export interface ForgotPasswordCredentials {
  email: string;
}
