import React, {useRef, useState, useEffect} from 'react';
import './App.css';
import axios from 'axios';
import {marked} from 'marked';
import DOMPurify from "dompurify";

const API = 'http://localhost:5000/api';

function formatDate(date: any) {
    const h = "0" + date.getHours();
    const m = "0" + date.getMinutes();

    return `${h.slice(-2)}:${m.slice(-2)}`;
}

interface MessageProps {
    name: string;
    time: string;
    content: string;
    left?: boolean;
    backgroundImage?: string;
}

const Message: React.FC<MessageProps> = (props: MessageProps) => {
    const {
        name,
        time,
        content,
        left = true,
        backgroundImage = ""
    } = props;

    const [sanitizedContent, setSanitizedContent] = useState('');

    useEffect(() => {
        const parseContent = async () => {
            const parsed = await marked.parse(content);
            setSanitizedContent(DOMPurify.sanitize(parsed));
        };
        parseContent().then(r => {});
    }, [content]);

    return (
        <div className={"message " + (left ? "left-message" : "right-message")}>
            <div
                className="message-img"
                style={{backgroundImage: backgroundImage}}
            ></div>

            <div className="message-bubble">
                <div className="message-info">
                    <div className="message-info-name">{name}</div>
                    <div className="message-info-time">{time}</div>
                </div>

                <div className="message-text">
                    <div dangerouslySetInnerHTML={{__html: sanitizedContent}}/>
                </div>
            </div>

        </div>
    )
}


const App = () => {
    const inputRef = useRef({} as HTMLInputElement);

    const [messages, setMessages] = useState<MessageProps[]>([]);

    const [isEditable, setIsEditable] = useState(true);

    const addMessage = (message: MessageProps) => {
        setMessages(prevMessages => [...prevMessages, message]); // WARNING
    };

    useEffect(() => {
        axios.get(API + '/get/all_messages').then(response => {
            setMessages(response.data.map((msg: { role: string; content: any; }) => {
                return {
                    name: msg.role == 'assistant' ? 'Bot' : 'Amias',
                    content: msg.content,
                    time: '??:??',
                    left: msg.role == 'assistant',
                }
            }));
        });
    }, []);

    const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();

        let messageText = inputRef.current.value;
        if (!messageText) {
            console.debug("Input text is required");
            return;
        }

        addMessage({
            name: 'Amias',
            time: formatDate(new Date()),
            content: messageText,
            left: false
        });
        inputRef.current.value = "";

        setIsEditable(false);

        // Ask and wait for answers from DeepSeek.
        axios.post(API + '/post/user_answer', {
            name: 'Amias',
            content: messageText,
        })
            .then((response) => {
                setIsEditable(true);

                addMessage({
                    name: 'Bot',
                    time: formatDate(new Date()),
                    content: response.data.content,
                    left: true
                });
            })
            .catch((error) => {
                if (error.response) {
                    // Server responded with a status other than 2xx
                    console.log(error.response.data);
                    console.log(error.response.status);
                } else if (error.request) {
                    // Request was made but no response received
                    console.log('No response received', error.request);
                } else {
                    // Something else happened
                    console.log('Error', error.message);
                }
            });
    };

    return (
        <div className="messager-whole-container">
            <div className="messager">
                <div className="messager-header">
                    <div className="messager-header-title">
                        <i className="fas fa-comment-alt"></i> Demo
                    </div>
                    <div className="messager-header-options">
                        <span><i className="fas fa-cog"></i></span>
                    </div>
                </div>

                <div className="messager-chat">
                    {messages.map(({name, time, content, left, backgroundImage}, index) => (
                        <Message name={name} time={time} content={content} left={left}
                                 backgroundImage={backgroundImage} key={index}/>
                    ))}
                </div>

                <form className="messager-inputarea" onSubmit={onSubmit}>
                    <input type="text" className="messager-input" placeholder="Enter your message..." ref={inputRef}
                           readOnly={!isEditable}/>
                    <button type="submit" className="messager-send-btn">Send</button>
                </form>
            </div>
        </div>
    );
}

export default App;
