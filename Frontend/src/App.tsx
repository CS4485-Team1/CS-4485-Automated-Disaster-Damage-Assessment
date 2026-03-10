import { useMemo, useState } from "react";
import "./App.css";

type DamageLevel = "noDamage" | "minorDamage" | "severeDamage";

type PropertyPoint = {
  id: string;
  damageLevel: DamageLevel;
  row: number;
  col: number;
};

const PROPERTIES: PropertyPoint[] = [
  {
    id: "p1",
    damageLevel: "noDamage",
    row: 0,
    col: 0,
  },
  {
    id: "p2",
    damageLevel: "minorDamage",
    row: 0,
    col: 1,
  },
  {
    id: "p3",
    damageLevel: "severeDamage",
    row: 0,
    col: 2,
  },
  {
    id: "p4",
    damageLevel: "minorDamage",
    row: 1,
    col: 0,
  },
  {
    id: "p5",
    damageLevel: "noDamage",
    row: 1,
    col: 1,
  },
  {
    id: "p6",
    damageLevel: "severeDamage",
    row: 1,
    col: 2,
  },
];

type ChatMessage = {
  id: number;
  sender: "user" | "assistant";
  text: string;
};

function App() {
  const [selectedDisaster, setSelectedDisaster] = useState<string | null>(null);
  const [damageFilter, setDamageFilter] = useState<{
    noDamage: boolean;
    minorDamage: boolean;
    severeDamage: boolean;
  }>({
    noDamage: true,
    minorDamage: true,
    severeDamage: true,
  });
  const [selectedPropertyId, setSelectedPropertyId] = useState<string>(
    PROPERTIES[2].id,
  );
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([
    {
      id: 1,
      sender: "assistant",
      text: "Ask me about damage patterns, affected areas, or overall impact.",
    },
  ]);

  const selectedProperty = useMemo(
    () => PROPERTIES.find((p) => p.id === selectedPropertyId) ?? PROPERTIES[0],
    [selectedPropertyId],
  );

  const filteredProperties = useMemo(
    () =>
      PROPERTIES.filter((p) => {
        if (p.damageLevel === "noDamage") return damageFilter.noDamage;
        if (p.damageLevel === "minorDamage") return damageFilter.minorDamage;
        return damageFilter.severeDamage;
      }),
    [damageFilter],
  );

  const handleToggleDamage = (level: DamageLevel) => {
    setDamageFilter((prev) => {
      const next = { ...prev };
      if (level === "noDamage") next.noDamage = !prev.noDamage;
      if (level === "minorDamage") next.minorDamage = !prev.minorDamage;
      if (level === "severeDamage") next.severeDamage = !prev.severeDamage;
      if (!next.noDamage && !next.minorDamage && !next.severeDamage) {
        return prev;
      }
      return next;
    });
  };

  const handleSendChat = () => {
    const trimmed = chatInput.trim();
    if (!trimmed) return;

    const nextId = chatMessages.length
      ? chatMessages[chatMessages.length - 1].id + 1
      : 1;

    const userMessage: ChatMessage = {
      id: nextId,
      sender: "user",
      text: trimmed,
    };

    const assistantMessage: ChatMessage = {
      id: nextId + 1,
      sender: "assistant",
      text: `This is a placeholder analysis for "${trimmed}". Once the model is connected, this area will summarize damage patterns and affected properties for the selected disaster.`,
    };

    setChatMessages((prev) => [...prev, userMessage, assistantMessage]);
    setChatInput("");
  };

  const renderHouse = (property: PropertyPoint) => {
    const isVisible = filteredProperties.some((p) => p.id === property.id);
    if (!isVisible) {
      return <div key={property.id} className="map-house empty-slot" />;
    }

    const damageClass =
      property.damageLevel === "noDamage"
        ? "no-damage"
        : property.damageLevel === "minorDamage"
          ? "minor-damage"
          : "severe-damage";

    return (
      <button
        key={property.id}
        type="button"
        className={`map-house ${damageClass}${
          property.id === selectedPropertyId ? " selected" : ""
        }`}
        onClick={() => setSelectedPropertyId(property.id)}
        aria-label={`Property – ${damageClass.replace("-", " ")}`}
      />
    );
  };

  const row0 = PROPERTIES.filter((p) => p.row === 0).sort(
    (a, b) => a.col - b.col,
  );
  const row1 = PROPERTIES.filter((p) => p.row === 1).sort(
    (a, b) => a.col - b.col,
  );

  return (
    <div className="app">
      <header className="app-header">
        <div className="app-header-left">
          <h1 className="app-title">Disaster Assessment Dashboard</h1>
          <p className="app-subtitle">Vision–Language Model Powered</p>
        </div>
        <div className="app-header-right">
          <button
            className="header-button secondary"
            type="button"
            onClick={() => {
              if (!selectedDisaster) {
                setSelectedDisaster("Disaster not yet selected");
              }
            }}
          >
            Select Disaster
          </button>
          <button className="header-button primary" type="button">
            Upload Imagery
          </button>
        </div>
      </header>

      <main className="app-main">
        <section className="left-column">
          <section className="panel imagery-panel">
            <div className="panel-header">
              <h2>Pre/Post Disaster Imagery</h2>
            </div>
            <div className="imagery-grid">
              <div className="imagery-card">
                <div className="imagery-placeholder before" />
                <div className="imagery-label">Before – simulated view</div>
              </div>
              <div className="imagery-card">
                <div className="imagery-placeholder after" />
                <div className="imagery-label">After – simulated view</div>
              </div>
            </div>
            <div className="imagery-details">
              <div className="imagery-pill">
                {selectedDisaster ?? "No disaster selected"}
              </div>
              <div className="imagery-meta">
                <div className="imagery-meta-title">Selected property</div>
                <div className="imagery-meta-damage">
                  Predicted damage:{" "}
                  <span className={`damage-tag ${selectedProperty.damageLevel}`}>
                    {selectedProperty.damageLevel === "noDamage" && "No Damage"}
                    {selectedProperty.damageLevel === "minorDamage" &&
                      "Minor Damage"}
                    {selectedProperty.damageLevel === "severeDamage" &&
                      "Severe Damage"}
                  </span>
                </div>
              </div>
            </div>
          </section>

          <section className="panel legend-panel">
            <div className="panel-header">
              <h2>Damage Filters</h2>
            </div>
            <ul className="legend-list">
              <li
                className={`legend-toggle${
                  damageFilter.noDamage ? "" : " inactive"
                }`}
                onClick={() => handleToggleDamage("noDamage")}
              >
                <span className="legend-dot no-damage" />
                <span>No Damage</span>
              </li>
              <li
                className={`legend-toggle${
                  damageFilter.minorDamage ? "" : " inactive"
                }`}
                onClick={() => handleToggleDamage("minorDamage")}
              >
                <span className="legend-dot minor-damage" />
                <span>Minor Damage</span>
              </li>
              <li
                className={`legend-toggle${
                  damageFilter.severeDamage ? "" : " inactive"
                }`}
                onClick={() => handleToggleDamage("severeDamage")}
              >
                <span className="legend-dot severe-damage" />
                <span>Severe Damage</span>
              </li>
            </ul>
          </section>
        </section>

        <section className="right-column">
          <section className="panel map-panel">
            <div className="panel-header">
              <h2>Property Damage Map</h2>
            </div>
            <div className="map-container">
              <div className="map-toolbar">
                <button className="map-button" type="button">
                  +
                </button>
                <button className="map-button" type="button">
                  −
                </button>
              </div>
              <div className="map-placeholder">
                <div className="map-houses-row">
                  {row0.map((property) => renderHouse(property))}
                </div>
                <div className="map-houses-row">
                  {row1.map((property) => renderHouse(property))}
                </div>
              </div>
              <div className="map-legend-floating">
                <div className="legend-title">Damage</div>
                <div className="legend-row">
                  <span className="legend-dot no-damage" />
                  <span>No Damage</span>
                </div>
                <div className="legend-row">
                  <span className="legend-dot minor-damage" />
                  <span>Minor Damage</span>
                </div>
                <div className="legend-row">
                  <span className="legend-dot severe-damage" />
                  <span>Severe Damage</span>
                </div>
              </div>
            </div>
            <div className="map-legend-bottom">
              <span className="legend-item">
                <span className="legend-dot no-damage" />
                No Damage
              </span>
              <span className="legend-item">
                <span className="legend-dot minor-damage" />
                Minor Damage
              </span>
              <span className="legend-item">
                <span className="legend-dot severe-damage" />
                Severe Damage
              </span>
            </div>
          </section>
        </section>
      </main>

      
<section className="chat-container">
  <div className="chat-messages">
    {chatMessages.map((message) => (
      <div
        key={message.id}
        className={`message-wrapper ${message.sender === "user" ? "user-wrapper" : "assistant-wrapper"}`}
      >
        {/* Only show the AI icon for assistant messages */}
        {message.sender === "assistant" && (
          <div className="assistant-icon" title="AI Assistant">AI</div>
        )}
        
        <div className={`chat-bubble ${message.sender}`}>
          {message.text}
        </div>
      </div>
    ))}
  </div>

  <div className="chat-input-area">
    {/* Refined Quick Actions to help with Capstone testing */}
    <div className="quick-actions">
      <button type="button" onClick={() => setChatInput("Analyze severe damage areas")}>
        Analyze Severe Damage
      </button>
      <button type="button" onClick={() => setChatInput("Show overall building damage")}>
        Show Overall Building Damage
      </button>
      <button type="button" onClick={() => setChatInput("Number of buildings affected")}>
        Show Number of Buildings Affected
      </button>
    </div>

    <div className="chat-input-row">
      <input
        className="chat-input"
        type="text"
        value={chatInput}
        onChange={(event) => setChatInput(event.target.value)}
        placeholder="Ask about damage patterns..."
        onKeyDown={(event) => {
          if (event.key === "Enter") {
            event.preventDefault();
            handleSendChat();
          }
        }}
      />
      <button
        className="chat-send-button"
        type="button"
        onClick={handleSendChat}
      >
        Send
      </button>
    </div>
  </div>
</section>
    </div>
  );
}

export default App;
