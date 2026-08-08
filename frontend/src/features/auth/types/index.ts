export interface User {
  user_id: string;
  email: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}
