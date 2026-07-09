<?php
header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => 'Method not allowed']);
    exit;
}

$honey = trim($_POST['_honey'] ?? '');
if ($honey !== '') {
    // Bots fill hidden fields; pretend success without sending anything.
    echo json_encode(['success' => true]);
    exit;
}

$name = trim($_POST['name'] ?? '');
$email = trim($_POST['email'] ?? '');
$interesse = trim($_POST['interesse'] ?? '');
$nachricht = trim($_POST['nachricht'] ?? '');

if ($name === '' || $nachricht === '' || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => 'Bitte alle Pflichtfelder gültig ausfüllen.']);
    exit;
}

$to = 'michael@codeundlicht.at';
$subject = 'Neue Projektanfrage über die Website';

$body = "Neue Anfrage über das Kontaktformular auf codeundlicht.at\n\n";
$body .= "Name: $name\n";
$body .= "E-Mail: $email\n";
$body .= "Interesse: $interesse\n\n";
$body .= "Nachricht:\n$nachricht\n";

$safeEmail = str_replace(["\r", "\n"], '', $email);
$headers = [
    'From: Code und Licht Website <noreply@codeundlicht.at>',
    'Reply-To: ' . $safeEmail,
    'Content-Type: text/plain; charset=UTF-8',
];

$sent = mail($to, $subject, $body, implode("\r\n", $headers));

if ($sent) {
    echo json_encode(['success' => true]);
} else {
    http_response_code(500);
    echo json_encode(['success' => false, 'message' => 'Nachricht konnte nicht gesendet werden.']);
}
