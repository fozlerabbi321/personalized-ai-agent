export class ApiError extends Error {
  constructor(
    public status: number,
    public message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = "ApiError";
  }
}

class ApiClient {
  private readonly baseUrl: string;
  private tokenGetter: (() => string | null) | null = null;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  public setTokenGetter(getter: () => string | null): void {
    this.tokenGetter = getter;
  }

  private getHeaders(auth: boolean, contentType = "application/json"): HeadersInit {
    const headers: Record<string, string> = {};
    if (contentType) {
      headers["Content-Type"] = contentType;
    }
    if (auth && this.tokenGetter) {
      const token = this.tokenGetter();
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }
    return headers;
  }

  private async parseError(res: Response): Promise<ApiError> {
    try {
      const data = await res.json();
      return new ApiError(
        res.status,
        data.detail || data.message || "An unexpected error occurred",
        data
      );
    } catch {
      return new ApiError(res.status, res.statusText || "Request failed");
    }
  }

  public async get<T>(path: string, auth = true): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "GET",
      headers: this.getHeaders(auth),
    });
    if (!res.ok) {
      throw await this.parseError(res);
    }
    return res.json() as Promise<T>;
  }

  public async post<T>(path: string, body: unknown, auth = true): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "POST",
      headers: this.getHeaders(auth),
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      throw await this.parseError(res);
    }
    return res.json() as Promise<T>;
  }

  public async delete(path: string, auth = true): Promise<void> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      method: "DELETE",
      headers: this.getHeaders(auth),
    });
    if (!res.ok) {
      throw await this.parseError(res);
    }
  }

  public getBaseUrl(): string {
    return this.baseUrl;
  }
}

export const apiClient = new ApiClient(
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
);
