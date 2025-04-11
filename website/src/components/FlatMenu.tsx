import React from "react"

import '../styles/flatmenu.css'


export interface FMItemProps {
    content: any;
    onClick?: () => void;
}

const MessageFlatMenuItem: React.FC<FMItemProps> = ({content, onClick}) => {
    return (
        <li className="flatmenu-item" onClick={onClick}>
            {content}
        </li>
    )
}

const FlatMenu: React.FC<{ items: FMItemProps[] }> = ({items}) => {
    return (
        <ul className="flat-menu">
            {items.map(({content, onClick}, index) => {
                return <MessageFlatMenuItem key={index} content={content} onClick={onClick}/>
            })}
        </ul>
    )
}

export default FlatMenu