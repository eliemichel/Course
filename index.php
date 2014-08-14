<?php

// OPTIONS //
$filename = 'test'; // text file to process (in src/ directory)
$tplname  = 'default'; // template file (in tpl/ directory)
/////////////

// List of keywords. Must be in lower case.
$keywords = array(
	'altitude', 'année', 'vallée', 'difficulté', 'départ', 'refuge', 'temps', 'dénivelée', 'temps', 'groupe', 'souvenirs'
);



echo("Loading file $filename...\n");

$src = file_get_contents("src/$filename");


echo("Parsing input file...\n");

$keyword = join($keywords, '|');
$r = "/^($keyword) *\: */i";

$lines = split("\n", $src);

$cur = 'titre';
$data = array('titre' => '');
foreach ($keywords as $k) {
	$data[$k] = '';
}

foreach ($lines as $l) {
	$l = preg_replace_callback(
		$r,
		function ($matches) use (&$cur) {
			$cur = strtolower($matches[1]);
			return '';
		},
		$l
	);
	$data[$cur] .= "$l\n";
}

foreach ($data as $key => $value) {
	$data[$key] = trim($value, "\n");
}

preg_replace_callback(
	"/^ *(.*)(\n*\((.*)\))?/",
	function ($matches) use (&$data) {
		$data['titre'] = $matches[1];
		$data['voie'] = $matches[3];
	},
	$data['titre']
);


echo("Loading template $tplname...\n");

$tpl = file_get_contents("tpl/$tplname.svg");


echo("Building vectorial image...\n");

foreach ($data as $key => $value) {
	$tpl = preg_replace("/&lt;$key&gt;/", htmlspecialchars($value), $tpl);
}

file_put_contents("output/$filename.svg", $tpl);


echo("Output final image in output/$filename.png...\n");

exec("inkscape output/$filename.svg -e output/$filename.png");

echo("Done.\n");
