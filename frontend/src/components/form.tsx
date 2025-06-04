import React from 'react'
import { Input } from './ui/input'
import { Button } from './ui/button'

interface FormProps {
  url: string;
  setUrl: (url: string) => void;
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  loading: boolean;
}

const Form = ({url, setUrl, handleSubmit, loading}: FormProps) => {
  return (
    <>
          <form onSubmit={handleSubmit} className="w-full max-w-md flex flex-col gap-y-4 items-center">
        <Input
          placeholder="Enter website URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="w-full bg-gray-800/50 text-white placeholder-gray-500 rounded-2xl p-4 pr-12 resize-none border border-gray-700/50 focus:border-cyan-400/50 focus:outline-none focus:ring-2 focus:ring-cyan-400/20  text-base transition-all duration-200"
          required
        />
        <Button
          disabled={loading}
          className={`w-fit bg-gradient-to-r from-cyan-400 to-blue-500 text-white font-semibold py-4 px-6 rounded-2xl disabled:opacity-40 disabled:cursor-not-allowed hover:scale-[1.02] transition-all duration-200 shadow-lg hover:shadow-cyan-500/25 flex items-center justify-center space-x-2 ${
            loading ? "bg-gray-400" : ""
          }`}
        >
          {loading ? "Cloning..." : "Clone Website"}
        </Button>
      </form>
    </>
  )
}

export default Form
