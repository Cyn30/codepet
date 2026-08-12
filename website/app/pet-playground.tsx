"use client";

import { useState } from "react";

const pets = [
  ["Ragdoll", "cat-0"], ["Devon Rex", "cat-1"], ["Golden Shaded", "cat-2"],
  ["Golden Retriever", "dog-0"], ["German Shepherd", "dog-1"], ["Scottish Collie", "dog-2"],
];

export function PetPlayground() {
  const [selected, setSelected] = useState(0);
  const [mode, setMode] = useState("RESTING");
  const [message, setMessage] = useState("Ready for your next commit?");
  const [visible, setVisible] = useState(true);

  function act(nextMode: string, nextMessage: string) {
    setMode(nextMode);
    setMessage(nextMessage);
  }

  return (
    <div className="playground" aria-label="Interactive CodePet preview">
      <div className="desktop-bar"><span /><span /><span /><b>CODEPET DESKTOP</b><div>SHOW <button aria-label="Show or hide pet" className={visible ? "switch on" : "switch"} onClick={() => setVisible(!visible)}><i /></button></div></div>
      <div className="desktop-scene">
        <div className="cloud c1"/><div className="cloud c2"/>
        {visible ? <button className={`hero-pet ${pets[selected][1]} ${mode === "WALKING" ? "walking" : ""}`} aria-label={`Pet ${pets[selected][0]}`} onClick={() => act("HAPPY", "That feels nice!")} /> : <div className="pet-hidden">Your pet is resting off-screen.</div>}
        {visible && <div className="speech">{message}</div>}
        {mode === "CAGED" && visible && <div className="cage" aria-hidden="true"><i/><i/><i/><i/><i/></div>}
        <div className="ground"><span/><span/><span/></div>
      </div>
      <div className="pet-console">
        <div className="stats"><div><span>{pets[selected][0]}</span><b>Byte · LV. 7</b></div><div><span>XP</span><b>184 / 231</b></div><div><span>FOOD</span><b>3 snacks</b></div></div>
        <div className="action-row">
          <button onClick={() => act("RESTING", "Nap time...")}>Rest</button>
          <button onClick={() => act("WALKING", "Adventure time!")}>Walk</button>
          <button onClick={() => act("CAGED", "Cozy and safe.")}>Cage</button>
          <button onClick={() => act("FED", "Delicious!")}>Feed</button>
        </div>
        <div className="breed-row" aria-label="Choose a breed">
          {pets.map(([name], index) => <button key={name} title={name} className={selected === index ? "selected" : ""} onClick={() => { setSelected(index); setMessage(`Hello, ${name}!`); }}>{index + 1}</button>)}
        </div>
      </div>
    </div>
  );
}
