import React, {useEffect, useState} from "react"
import {marked} from "marked"
import DOMPurify from "dompurify"

export interface MessageProps {
    name: string;
    time: string;
    content: string;
    left?: boolean;
    backgroundImage?: string;
    children?: React.ReactNode;
}

const Message: React.FC<MessageProps> = (
    {
        name,
        time,
        content,
        left = true,
        backgroundImage = "",
        children,
    }: MessageProps) => {

    const [sanitizedContent, setSanitizedContent] = useState('')

    useEffect(() => {
        const parseContent = async () => {
            const parsed = await marked.parse(content)
            setSanitizedContent(DOMPurify.sanitize(parsed))
        }
        parseContent().then(() => {
        })
    }, [content])

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

                {children}
            </div>
        </div>
    )
}


export default Message