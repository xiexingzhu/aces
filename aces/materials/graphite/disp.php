<?php

$potential="
pair_style        tersoff
pair_coeff      * * $home/potentials/BNC.tersoff C
";
$dump="
dump_modify dump1 element C
";
function structure(){
	$home=dirname(__FILE__);
	require_once("$home/../../config.php");
	$php="$PHP_HOME/php";
 shell_exec("$php $home/structure.php");
	echo"
read_data structure
";
}
?>