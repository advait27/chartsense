import React, { useState, useRef, useEffect } from 'react';
import { MessageSquare, Send, Trash2, Loader } from 'lucide-react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || '/api';

const ChatInterface = ({ analysisData }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message when chat is opened with analysis data
    if (analysisData && messages.length === 0) {
      setMessages([
        {
          role: 'assistant',
          content: '👋 Hello! I\'m here to help you understand your chart analysis. Feel free to ask me anything about the market structure, momentum, trading strategies, or any specific aspect of the analysis.',
          timestamp: new Date().toISOString()
        }
      ]);
    }
  }, [analysisData, messages.length]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        session_id: sessionId,
        message: inputMessage,
        analysis_context: analysisData
      });

      const assistantMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: response.data.timestamp
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        role: 'assistant',
        content: '❌ Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = async () => {
    try {
      await axios.delete(`${API_URL}/chat/${sessionId}`);
      setMessages([
        {
          role: 'assistant',
          content: '👋 Chat cleared! How can I help you with your chart analysis?',
          timestamp: new Date().toISOString()
        }
      ]);
    } catch (error) {
      console.error('Clear chat error:', error);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit'
    });
  };

  return (
    <div className="chat-interface">
      <div className="chat-header">
        <div className="chat-header-title">
          <MessageSquare size={20} />
          <h3>Ask About Your Analysis</h3>
        </div>
        <button 
          className="chat-clear-button"
          onClick={clearChat}
          disabled={messages.length === 0}
          title="Clear chat"
        >
          <Trash2 size={16} />
        </button>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="chat-empty-state">
            <MessageSquare size={48} />
            <p>No messages yet</p>
            <span>Ask anything about your chart analysis</span>
          </div>
        ) : (
          messages.map((message, index) => (
            <div 
              key={index} 
              className={`chat-message ${message.role} ${message.isError ? 'error' : ''}`}
            >
              <div className="message-content">
                {message.content}
              </div>
              <div className="message-timestamp">
                {formatTimestamp(message.timestamp)}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="chat-message assistant loading">
            <div className="message-content">
              <Loader size={16} className="spinning" />
              <span>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <textarea
          ref={inputRef}
          className="chat-input"
          placeholder="Ask about trends, entry points, risk levels..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isLoading}
          rows={1}
        />
        <button 
          className="chat-send-button"
          onClick={handleSendMessage}
          disabled={!inputMessage.trim() || isLoading}
        >
          {isLoading ? <Loader size={20} className="spinning" /> : <Send size={20} />}
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;
