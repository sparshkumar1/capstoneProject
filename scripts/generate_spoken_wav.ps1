Add-Type -AssemblyName System.Speech
$speak = New-Object System.Speech.Synthesis.SpeechSynthesizer
$speak.SetOutputToWaveFile("tests\test_candidate_hash_table_answer.wav")
$speak.Speak("A hash table handles collisions using separate chaining where each bucket contains a linked list of elements, or open addressing such as linear probing where we search for the next available slot when a collision occurs.")
$speak.Dispose()
Write-Host "Generated tests\test_candidate_hash_table_answer.wav successfully"
