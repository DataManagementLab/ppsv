# create test database
$title    = 'Creating Test Database'
$question = 'Do you want to create a prefilled Database? This will delete all current Data!'
$choices  = '&Yes', '&No'

$decision = $Host.UI.PromptForChoice($title, $question, $choices, 1)
if ($decision -eq 0) {
    Write-Host 'confirmed'
    python ..\ppsv\manage.py flush --noinput
} else {
    Write-Host 'cancelled'
    return
}

py ..\ppsv\manage.py runscript createTestDB