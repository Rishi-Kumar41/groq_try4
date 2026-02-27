import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ChatService, ChatResponse } from '../../services/chat.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [FormsModule, CommonModule],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss']
})
export class ChatComponent {
  prompt = '';
  system = 'You are a helpful assistant.';
  temperature = 0.7;
  maxTokens = 512;

  loading = false;
  error = '';
  output = '';

  constructor(private chatService: ChatService) {}

  onSend() {
    this.error = '';
    this.output = '';
    const trimmed = this.prompt.trim();
    if (!trimmed) {
      this.error = 'Please enter a prompt.';
      return;
    }

    this.loading = true;
    this.chatService.sendPrompt({
      prompt: trimmed,
      system: this.system,
      temperature: this.temperature,
      max_tokens: this.maxTokens
    }).subscribe({
      next: (res: ChatResponse) => {
        this.output = res.output;
        this.loading = false;
      },
      error: (err: Error) => {
        this.error = err.message || 'Something went wrong.';
        this.loading = false;
      }
    });
  }
}
