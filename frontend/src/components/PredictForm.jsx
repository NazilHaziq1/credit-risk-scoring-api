import { useState } from 'react'

const REPAYMENT_OPTIONS = [
  { value: -2, label: '-2 — No consumption' },
  { value: -1, label: '-1 — Paid in full' },
  { value: 0,  label: '0 — Revolving credit used' },
  { value: 1,  label: '1 — 1 month late' },
  { value: 2,  label: '2 — 2 months late' },
  { value: 3,  label: '3 — 3 months late' },
  { value: 4,  label: '4 — 4 months late' },
  { value: 5,  label: '5 — 5 months late' },
  { value: 6,  label: '6+ months late' },
]

const MONTHS = ['Sep', 'Aug', 'Jul', 'Jun', 'May', 'Apr']

const DEFAULT_VALUES = {
  credit_limit: 50000, sex: 2, education: 2, marriage: 2, age: 30,
  pay_0: -1, pay_2: -1, pay_3: -1, pay_4: -1, pay_5: -1, pay_6: -1,
  bill_amt1: 5000, bill_amt2: 4800, bill_amt3: 4600,
  bill_amt4: 4400, bill_amt5: 4200, bill_amt6: 4000,
  pay_amt1: 2000, pay_amt2: 1800, pay_amt3: 1600,
  pay_amt4: 1400, pay_amt5: 1200, pay_amt6: 1000,
}

const s = {
  section: {
    background: '#fff', border: '1px solid #e5e7eb',
    borderRadius: 10, padding: '20px 24px', marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 13, fontWeight: 700, color: '#5c6bc0',
    letterSpacing: 1, marginBottom: 16, textTransform: 'uppercase',
  },
  grid2: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px 24px' },
  grid3: { display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px 24px' },
  label: { display: 'block', fontSize: 12, fontWeight: 600, color: '#555', marginBottom: 4 },
  input: {
    width: '100%', padding: '8px 10px', border: '1px solid #d1d5db',
    borderRadius: 6, fontSize: 14, outline: 'none', background: '#fafafa',
  },
  select: {
    width: '100%', padding: '8px 10px', border: '1px solid #d1d5db',
    borderRadius: 6, fontSize: 14, outline: 'none', background: '#fafafa',
  },
}

function Field({ label, children }) {
  return (
    <div>
      <label style={s.label}>{label}</label>
      {children}
    </div>
  )
}

export default function PredictForm({ onSubmit, loading }) {
  const [values, setValues] = useState(DEFAULT_VALUES)

  const set = (key, val) => setValues(v => ({ ...v, [key]: val }))
  const num = (key, val) => set(key, Number(val))

  const handleSubmit = e => {
    e.preventDefault()
    onSubmit(values)
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* Personal Info */}
      <div style={s.section}>
        <div style={s.sectionTitle}>Personal Information</div>
        <div style={s.grid3}>
          <Field label="Credit Limit (NTD)">
            <input style={s.input} type="number" min={1} value={values.credit_limit}
              onChange={e => num('credit_limit', e.target.value)} required />
          </Field>
          <Field label="Age">
            <input style={s.input} type="number" min={18} max={100} value={values.age}
              onChange={e => num('age', e.target.value)} required />
          </Field>
          <Field label="Sex">
            <select style={s.select} value={values.sex} onChange={e => num('sex', e.target.value)}>
              <option value={1}>Male</option>
              <option value={2}>Female</option>
            </select>
          </Field>
          <Field label="Education">
            <select style={s.select} value={values.education} onChange={e => num('education', e.target.value)}>
              <option value={1}>Graduate School</option>
              <option value={2}>University</option>
              <option value={3}>High School</option>
              <option value={4}>Other</option>
            </select>
          </Field>
          <Field label="Marital Status">
            <select style={s.select} value={values.marriage} onChange={e => num('marriage', e.target.value)}>
              <option value={1}>Married</option>
              <option value={2}>Single</option>
              <option value={3}>Other</option>
            </select>
          </Field>
        </div>
      </div>

      {/* Repayment Status */}
      <div style={s.section}>
        <div style={s.sectionTitle}>Repayment Status (last 6 months)</div>
        <div style={s.grid3}>
          {MONTHS.map((month, i) => {
            const key = i === 0 ? 'pay_0' : `pay_${i + 1}`
            return (
              <Field key={key} label={month}>
                <select style={s.select} value={values[key]} onChange={e => num(key, e.target.value)}>
                  {REPAYMENT_OPTIONS.map(o => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                  ))}
                </select>
              </Field>
            )
          })}
        </div>
      </div>

      {/* Bill Amounts */}
      <div style={s.section}>
        <div style={s.sectionTitle}>Bill Statement Amount — NTD (last 6 months)</div>
        <div style={s.grid3}>
          {MONTHS.map((month, i) => {
            const key = `bill_amt${i + 1}`
            return (
              <Field key={key} label={month}>
                <input style={s.input} type="number" value={values[key]}
                  onChange={e => num(key, e.target.value)} required />
              </Field>
            )
          })}
        </div>
      </div>

      {/* Payment Amounts */}
      <div style={s.section}>
        <div style={s.sectionTitle}>Previous Payment Amount — NTD (last 6 months)</div>
        <div style={s.grid3}>
          {MONTHS.map((month, i) => {
            const key = `pay_amt${i + 1}`
            return (
              <Field key={key} label={month}>
                <input style={s.input} type="number" min={0} value={values[key]}
                  onChange={e => num(key, e.target.value)} required />
              </Field>
            )
          })}
        </div>
      </div>

      <button
        type="submit"
        disabled={loading}
        style={{
          width: '100%', padding: '14px', borderRadius: 8, border: 'none',
          background: loading ? '#9fa8da' : '#3f51b5',
          color: '#fff', fontSize: 16, fontWeight: 700, cursor: loading ? 'not-allowed' : 'pointer',
          transition: 'background 0.2s',
        }}
      >
        {loading ? 'Scoring…' : 'Score Applicant'}
      </button>
    </form>
  )
}
