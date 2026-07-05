import { SignupForm } from "../../../components/signup-form";
export default function Register() {
  return (
    <>
      <div className="min-h-screen bg-[#feffe6] flex items-center justify-center px-4">
        <div className="w-full max-w-sm">
          <SignupForm />
        </div>
      </div>
    </>
  );
}
