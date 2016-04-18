<?php

namespace PnX\TaxonomieBundle\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\Controller;
use Symfony\Component\HttpFoundation\BinaryFileResponse;

class DefaultController extends Controller {
    public function indexAction()
    {
        return new BinaryFileResponse('index.html');
    }
}
