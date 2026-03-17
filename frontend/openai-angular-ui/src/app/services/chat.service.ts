import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse, HttpHeaders } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface ChatRequest {
  prompt: string;
  system?: string;
  temperature?: number;
  max_tokens?: number;
}

export interface ChatResponse {
  output: string;
  provider: string;
  model: string;
}

@Injectable({ providedIn: 'root' })
export class ChatService {
  private baseUrl = 'http://localhost:8500';
  constructor(private http: HttpClient) {}

  sendPrompt(body: ChatRequest): Observable<ChatResponse> {
    const url = `${this.baseUrl}/api/chat`;
    const headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    return this.http.post<ChatResponse>(url, body, { headers })
      .pipe(catchError(this.handleError));
  }

  private handleError(err: HttpErrorResponse) {
    let msg = 'An unknown error occurred.';
    if (err.error?.detail) msg = err.error.detail;
    else if (err.message) msg = err.message;
    return throwError(() => new Error(msg));
  }
}
