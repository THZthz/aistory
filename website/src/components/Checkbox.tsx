import React from 'react'

import '../styles/checkbox.css'


const Checkbox: React.FC<{  }> = () => {
    return (
        <div className="checkbox-wrapper-32">
            <input type="checkbox" name="checkbox-32" id="checkbox-32"/>
            <label htmlFor="checkbox-32">
                Checkbox
            </label>
            <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                <path d="M 10 10 L 90 90" stroke="#000" stroke-dasharray="113" stroke-dashoffset="113"></path>
                <path d="M 90 10 L 10 90" stroke="#000" stroke-dasharray="113" stroke-dashoffset="113"></path>
            </svg>
        </div>
    )
}

export default Checkbox