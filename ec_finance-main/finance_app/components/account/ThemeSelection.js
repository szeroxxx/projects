import { CheckOutlined } from "@ant-design/icons";
import React, { useState } from "react";
function themName(theme){
if(theme=="black") return "Black";
else if(theme=="dark_orange") return "Dark orange";
else if(theme=="persian_green") return "Persian green";
else if(theme=="radical_red") return "Radical red";
else if(theme=="royal_blue") return "Royal blue";
else if(theme=="violet") return "Violet";
else if(theme=="pink") return "Pink";
}
const ThemeSelection = ({ data, form, fieldProps , disabled}) => {
  const themes = ["black", "dark_orange", "persian_green", "radical_red", "royal_blue", "violet", "pink"];
  const [selectedTheme, setTheme] = useState(data);
  return (
    <div className="theme-container" style={disabled ? {pointerEvents: "none", opacity: "0.4"} : {}}>
      {themes.map((theme, uid) => {
        return (
          <div key={uid} className="profile-box">
            <div
              className={`theme_${theme} commonFor_profile-box ${selectedTheme == theme ? "theme_"+theme+"_active " : ""}`}
              onClick={() => {
                setTheme(theme);
                const fieldsValues = {};
                fieldsValues[fieldProps.name] = theme;
                form.current.setFieldsValue(fieldsValues);
              }}
            >
            <p className="them-name">{themName(theme)}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
};
export default ThemeSelection;


//profile-box

/*<div key={uid} className="circle">
<span
  className={`theme_${theme} commonFor_circle ${selectedTheme == theme ? "active_circle" : ""}`}
  onClick={() => {
    setTheme(theme);

    const fieldsValues = {};
    fieldsValues[fieldProps.name] = theme;
    form.current.setFieldsValue(fieldsValues);
  }}
>
  <CheckOutlined className="active_circleIcon" />
</span>
</div>*/