"use client";

import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import styles from '../styles/Chat.module.css';
import { FaPaperPlane, FaMicrophone, FaChevronUp } from 'react-icons/fa';

async function getMessageResponse(content) {
    try {
        const encodedContent = encodeURIComponent(content);
        const response = await fetch(`http://localhost:8000/messages/${encodedContent}`, {
            method: 'GET',
            mode: 'cors',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        return data.response;
    } catch (error) {
        console.error('Error fetching message response:', error);
        throw error;
    }
}

function Chat() {
    const [messages, setMessages] = useState([
        {
            text: "Hi, I'm **PrAIvateSearch**, your fully local search engine. Powered by NextJS, FastAPI, Qdrant, Postgres and DuckDuckGo🪿",
            sender: 'bot',
        },
    ]);
    const [input, setInput] = useState('');
    
    const chatMessagesRef = useRef(null);
    
    const handleSendMessage = async () => {
        if (input.trim() === '') return;

        const newMessage = {
            text: input,
            sender: 'user',
        };

        setMessages((prevMessages) => [...prevMessages, newMessage]);
        setInput('');

        try {
            const botResponseText = await getMessageResponse(input);
            
            const botResponse = {
                text: botResponseText || "No response received",
                sender: 'bot'
            };
            
            setMessages((prevMessages) => [...prevMessages, botResponse]);
        } catch(error) {
            const errorResponse = {
                text: "Error reaching the server. Please check if the backend server is running on port 8000.",
                sender: 'bot'
            };
            
            setMessages((prevMessages) => [...prevMessages, errorResponse]);
            console.error("Error while handling message", error);
        }
    };

    useEffect(() => {
        if (chatMessagesRef.current) {
            chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
        }
    }, [messages]);
    
    const scrollToBottom = () => {
        if (chatMessagesRef.current) {
            chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
        }
    };

    // Custom renderer for markdown code blocks
    const renderers = {
        code: ({node, inline, className, children, ...props}) => {
            const match = /language-(\w+)/.exec(className || '');
            return !inline ? (
                <pre className={styles.codeBlock}>
                    <code className={match ? `language-${match[1]}` : ''} {...props}>
                        {children}
                    </code>
                </pre>
            ) : (
                <code className={styles.inlineCode} {...props}>
                    {children}
                </code>
            );
        }
    };

    return (
        <div className={styles.chatContainer}>
            <div className={styles.chatHeader}>PrAIvateSearch🪿</div>
            <div className={styles.chatMessages} ref={chatMessagesRef}>
                {messages.map((message, index) => (
                    <div
                        key={index}
                        className={`${styles.message} ${
                            message.sender === 'user' ? styles.userMessage : styles.botMessage
                        }`}
                    >
                        {message.sender === 'user' ? (
                            <div className={styles.messageText}>
                                {message.text}
                            </div>
                        ) : (
                            <div className={styles.messageText}>
                                <ReactMarkdown 
                                    components={renderers}
                                    className={styles.markdown}
                                >
                                    {message.text}
                                </ReactMarkdown>
                            </div>
                        )}
                    </div>
                ))}
            </div>
            
            <div className={styles.chatInputArea}>
                <input
                    type="text"
                    placeholder="Send a message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    className={styles.inputField}
                />
                <button onClick={handleSendMessage} className={styles.sendButton}>
                    <FaPaperPlane size="1.4em" />
                </button>
            </div>
            <button 
                onClick={scrollToBottom} 
                className={styles.sendButton} 
                style={{alignSelf: 'end', display: 'block', marginTop: '0.5em', padding: '4px'}}
            >
                <FaChevronUp size="1.2em" style={{transform: 'rotate(180deg)'}}/>
            </button>
        </div>
    );
}

export default Chat;