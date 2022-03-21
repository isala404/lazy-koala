import React from "react";
import "./loader.css";

export default function Loader(){
    return (
        <div className="center-div">
            <div className="lds-ellipsis">
                <div></div>
                <div></div>
                <div></div>
                <div></div>
            </div>
        </div>
    )
}