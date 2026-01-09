import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './Stage2.css';

function labelToName(label, labelToModel) {
  if (!labelToModel || !labelToModel[label]) return label;
  return labelToModel[label].split('/')[1] || labelToModel[label];
}

export default function Stage2({ rankings, labelToModel, aggregateRankings }) {
  const [activeTab, setActiveTab] = useState(0);

  if (!rankings || rankings.length === 0) {
    return null;
  }

  const active = rankings[activeTab];

  return (
    <div className="stage stage2">
      <h3 className="stage-title">Stage 2: Peer Rankings</h3>

      <h4>Reviewer Outputs</h4>
      <p className="stage-description">
        Each reviewer ranks the anonymized responses (Model A, B, C, etc.) and provides a short justification.
      </p>

      <div className="tabs">
        {rankings.map((rank, index) => (
          <button
            key={index}
            className={`tab ${activeTab === index ? 'active' : ''}`}
            onClick={() => setActiveTab(index)}
          >
            {rank.reviewer_model?.split('/')[1] || rank.reviewer_model}
          </button>
        ))}
      </div>

      <div className="tab-content">
        <div className="ranking-model">
          {active.reviewer_model}
        </div>

        {active.error && (
          <div className="parsed-ranking">
            <strong>Error:</strong> {active.error}
          </div>
        )}

        {active.ranking && active.ranking.length > 0 && (
          <div className="parsed-ranking">
            <strong>Ranking:</strong>
            <ol>
              {active.ranking.map((label, i) => (
                <li key={i}>
                  {labelToName(label, labelToModel)}
                </li>
              ))}
            </ol>
          </div>
        )}

        {active.justification && Object.keys(active.justification).length > 0 && (
          <div className="parsed-ranking">
            <strong>Justification:</strong>
            {Object.entries(active.justification).map(([label, text]) => (
              <div key={label} className="ranking-content markdown-content">
                <ReactMarkdown>
                  {`${labelToName(label, labelToModel)}: ${text}`}
                </ReactMarkdown>
              </div>
            ))}
          </div>
        )}

        {active.parse_status && active.parse_status !== 'parsed_json' && active.raw_text && (
          <div className="parsed-ranking">
            <strong>Raw Output (fallback used):</strong>
            <div className="ranking-content markdown-content">
              <ReactMarkdown>{active.raw_text}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>

      {aggregateRankings && aggregateRankings.length > 0 && (
        <div className="aggregate-rankings">
          <h4>Aggregate Rankings</h4>
          <p className="stage-description">
            Combined results across all peer evaluations (higher score is better):
          </p>
          <div className="aggregate-list">
            {aggregateRankings.map((agg, index) => (
              <div key={index} className="aggregate-item">
                <span className="rank-position">#{index + 1}</span>
                <span className="rank-model">
                  {agg.model.split('/')[1] || agg.model}
                </span>
                <span className="rank-score">
                  Score: {agg.score}
                </span>
                <span className="rank-count">
                  ({agg.votes} votes)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
