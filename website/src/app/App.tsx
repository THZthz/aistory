import React, {useRef, useState, useEffect} from 'react'
import axios from 'axios'

import Message, {MessageProps} from '../components/Message'
import FlatMenu from "../components/FlatMenu"
import FlatAccordion from "../components/FlatAccordion"

import '../styles/App.css'


const API = 'http://localhost:5000/api'


function formatDate(date: Date) {
    const h = "0" + date.getHours()
    const m = "0" + date.getMinutes()

    return `${h.slice(-2)}:${m.slice(-2)}`
}

const App = () => {
    const inputRef = useRef({} as HTMLInputElement)
    const messageEndRef = useRef({} as HTMLDivElement)

    const [messages, setMessages] = useState<MessageProps[]>([])

    const [isEditable, setIsEditable] = useState(true)

    const addMessage = (message: MessageProps) => {
        setMessages(prevMessages => [...prevMessages, message]) // WARNING
        messageEndRef.current.scrollIntoView()
    };

    useEffect(() => {
        axios.get(API + '/get/all_messages').then(response => {
            setMessages(response.data.map((msg: { role: string; content: any; }) => {
                return {
                    name: msg.role === 'assistant' ? 'Bot' : 'Amias',
                    content: msg.content,
                    time: '??:??',
                    left: msg.role === 'assistant',
                }
            }))
            messageEndRef.current.scrollIntoView()
        })
    }, [])

    const onSubmit = (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault()

        let messageText = inputRef.current.value
        if (!messageText) {
            console.debug("Input text is required");
            return;
        }

        addMessage({
            name: 'Amias',
            time: formatDate(new Date()),
            content: messageText,
            left: false
        })
        inputRef.current.value = ""

        setIsEditable(false)

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
                })
            })
            .catch((error) => {
                if (error.response) {
                    // Server responded with a status other than 2xx
                    console.log(error.response.data)
                    console.log(error.response.status)
                } else if (error.request) {
                    // Request was made but no response received
                    console.log('No response received', error.request)
                } else {
                    // Something else happened
                    console.log('Error', error.message)
                }
            })
    }

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

                    <Message name={'Ginny'} time={formatDate(new Date())} content={'Flat menu test:'}>
                        <FlatMenu items={[
                            {
                                onClick: () => console.log('Menu clicked'),
                                content: (
                                    <div>
                                        <svg className="menu-icon" viewBox="0 0 24 24">
                                            <path
                                                d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                                        </svg>
                                        Delete
                                    </div>
                                )
                            },
                            {
                                content: (
                                    <div>
                                        <svg className="menu-icon" viewBox="0 0 24 24">
                                            <path
                                                d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34c-.39-.39-1.02-.39-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
                                        </svg>
                                        Edit
                                    </div>
                                )
                            }
                        ]}/>
                    </Message>

                    <Message name={'Veyla'} time={formatDate(new Date())} content={'Flat accordion test:'}>
                        <FlatAccordion items={[
                            {
                                id: '1',
                                icon: "📅",
                                title: "Vely's Wearings",
                                subtitle: "All kind of things she wears",
                                meta: "3",
                                subItems: [
                                    {
                                        id: '1-1',
                                        title: 'Ravenfeather Broadbrim',
                                        subtitle: 'A worn yet elegant black broad-brimmed hat adorned with raven feathers at its edge. Stitched inside the brim lieth a stolen silver coin, for bribes or ale in dire need.'
                                    },
                                    {
                                        id: '1-2',
                                        title: 'Shadowstitch Doublet',
                                        subtitle: 'A deep indigo doublet, tight-fitted, with dark embroidery upon its face. Hidden pockets line the inner cloth, holding stolen rings and vials of venom.'
                                    }, {
                                        id: '1-3',
                                        title: 'Thief\'s Cloak',
                                        subtitle: 'A frayed but supple cloak of dusken grey, its hem marked with faint claw-scratches unseen. Within its folds lie a blade thin as a cicada\'s wing and false coins to distract the unwary.'
                                    }, {
                                        id: '1-4',
                                        title: 'Muted Leather Breeches',
                                        subtitle: 'Soft-tanned deerhide trousers, reinforced at the knees for climbing and creeping. A secret pouch on the right leg hides a set of loaded dice (\'lest the game play unfair\').'
                                    }, {
                                        id: '1-5',
                                        title: 'Catstep Softboots',
                                        subtitle: 'Soles lined with moss for silence, though they must be changed lest they reek. A slender lockpick (or toothpick, at need) is tucked inside the boot\'s embrace.'
                                    }, {
                                        id: '1-6',
                                        title: 'Gambler\'s Gloves',
                                        subtitle: 'Gloves of black lambskin, worn at the fingertips for nimble theft and cardplay.'
                                    }, {
                                        id: '1-7',
                                        title: 'Chain of the Hushed',
                                        subtitle: 'A silver chain bearing a hollow raven\'s skull, wherein lies a poison to still the tongue.'
                                    }
                                ]
                            },
                            {
                                id: '2',
                                icon: "🛒",
                                title: "Shopping List",
                                subtitle: "Milk, eggs, bread",
                                meta: "12:00",
                                subItems: [
                                    {
                                        id: '2-1',
                                        title: 'Items',
                                        subtitle: 'A4 papers, pens etc.'
                                    }
                                ]
                            },
                            {
                                id: '3',
                                icon: "📝",
                                title: "Work Report",
                                subtitle: "Complete quarterly data analysis",
                                meta: "15:00"
                            },
                            {
                                id: '4',
                                icon: "🏋️",
                                title: "Workout Plan",
                                subtitle: "Back training + 30 mins cardio",
                                meta: "18:30"
                            },
                            {
                                id: '5',
                                icon: "🎬",
                                title: "Movie Night",
                                subtitle: "Watch the new sci-fi movie",
                                meta: "20:00"
                            },
                            {
                                id: '6',
                                icon: "📚",
                                title: "Reading Time",
                                subtitle: "Continue reading 'The Design of Everyday Things'",
                                meta: "21:30"
                            },
                            {
                                id: '7',
                                icon: "💤",
                                title: "Bedtime",
                                subtitle: "Ensure 7 hours of sleep",
                                meta: "23:00"
                            }
                        ]}/>
                    </Message>

                    <Message name={'Veyla'} time={formatDate(new Date())} content={'I hope anyone is there...'} />

                    <div className="messager-end" ref={messageEndRef}></div>
                </div>

                <form className="messager-inputarea" onSubmit={onSubmit}>
                    <input type="text" className="messager-input" placeholder="Enter your message..." ref={inputRef}
                           readOnly={!isEditable}/>
                    <button type="submit" className="messager-send-btn">Send</button>
                </form>
            </div>
        </div>
    )
}

export default App
